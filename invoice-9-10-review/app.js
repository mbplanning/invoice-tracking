(function () {
  "use strict";

  var STORAGE = "ewa-dp-inv9-10-v2";
  var state = {
    inv9: null,
    inv10: null,
    view: 10,
    selected: null,
    page: 1,
    pdf: null,
    drawing: false,
    notes: loadNotes()
  };

  function $(id) { return document.getElementById(id); }

  function money(n) {
    var v = Number(n) || 0;
    var body = Math.abs(v).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    return (v < 0 ? "−$" : "$") + body;
  }

  function round2(n) {
    return Math.round((Number(n) + Number.EPSILON) * 100) / 100;
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function current() { return state.view === 10 ? state.inv10 : state.inv9; }

  function task(inv, number) {
    return inv.tasks.find(function (t) { return t.taskNumber === number; });
  }

  function key(number) { return state.view + ":" + number; }

  function loadNotes() {
    try {
      var parsed = JSON.parse(localStorage.getItem(STORAGE) || "null");
      return parsed && parsed.items ? parsed : { items: {} };
    } catch (e) {
      return { items: {} };
    }
  }

  function saveNotes() {
    localStorage.setItem(STORAGE, JSON.stringify({
      savedAt: new Date().toISOString(),
      items: state.notes.items
    }));
    flash("Notes saved");
  }

  function flash(text) {
    var el = $("status");
    el.hidden = false;
    el.textContent = text;
    clearTimeout(flash.t);
    flash.t = setTimeout(function () { el.hidden = true; }, 1200);
  }

  function getMark(number) { return state.notes.items[key(number)] || null; }

  function setMark(number, data) {
    if (!data) delete state.notes.items[key(number)];
    else {
      var t = task(current(), number);
      state.notes.items[key(number)] = Object.assign({
        taskNumber: number,
        taskName: t ? t.taskName : "",
        invoiceNumber: state.view,
        invoicePage: t ? t.invoicePage : 1,
        updatedAt: new Date().toISOString()
      }, data);
    }
    saveNotes();
    $("disc-count").textContent = String(Object.keys(state.notes.items).length);
  }

  function compare(number) {
    var curr = task(current(), number);
    if (!curr) return null;
    if (state.view === 10) {
      var prev = task(state.inv9, number);
      var changeAmount = round2(curr.totalBilled - prev.totalBilled);
      return {
        task: curr,
        prevLabel: "Invoice 9",
        currLabel: "Invoice 10",
        budget: curr.budget,
        budgetNote: curr.budgetNote || (prev.budget !== curr.budget
          ? "Printed task budget changed from " + money(prev.budget) + " on Invoice 9 to " + money(curr.budget) + " on Invoice 10."
          : ""),
        previousCumulativeAmount: prev.totalBilled,
        previousPercent: prev.printedPercent,
        currentInvoiceAmount: curr.currentInvoiceAmount,
        currentCumulativeAmount: curr.totalBilled,
        currentPercent: curr.printedPercent,
        changeAmount: changeAmount,
        changePercent: curr.printedPercent - prev.printedPercent,
        remainingAmount: curr.remainingAmount,
        remainingPercent: curr.budget ? Math.round((curr.remainingAmount / curr.budget) * 100) : 0,
        priorMismatch: Math.abs(curr.printedPriorBilled - prev.totalBilled) > 0.02,
        currentMismatch: Math.abs(curr.currentInvoiceAmount - changeAmount) > 0.02,
        printedPrior: curr.printedPriorBilled,
        independent: false
      };
    }
    var priorPct = curr.budget ? Math.round((curr.printedPriorBilled / curr.budget) * 100) : 0;
    return {
      task: curr,
      prevLabel: "Prior column on Invoice 9",
      currLabel: "Invoice 9",
      budget: curr.budget,
      budgetNote: "",
      previousCumulativeAmount: curr.printedPriorBilled,
      previousPercent: priorPct,
      currentInvoiceAmount: curr.currentInvoiceAmount,
      currentCumulativeAmount: curr.totalBilled,
      currentPercent: curr.printedPercent,
      changeAmount: curr.currentInvoiceAmount,
      changePercent: curr.printedPercent - priorPct,
      remainingAmount: curr.remainingAmount,
      remainingPercent: curr.budget ? Math.round((curr.remainingAmount / curr.budget) * 100) : 0,
      priorMismatch: false,
      currentMismatch: false,
      printedPrior: curr.printedPriorBilled,
      independent: true
    };
  }

  function billedNow(cmp) {
    return cmp.currentInvoiceAmount !== 0 || (state.view === 10 && cmp.changeAmount !== 0);
  }

  function renderIndex() {
    var inv = current();
    var host = $("task-index");
    host.innerHTML = "";
    var stage = null;
    inv.tasks.forEach(function (t) {
      var cmp = compare(t.taskNumber);
      if (t.stageName !== stage) {
        var label = document.createElement("p");
        label.className = "idx-stage";
        label.textContent = "St " + t.stage;
        host.appendChild(label);
        stage = t.stageName;
      }
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "idx-btn";
      if (state.selected === t.taskNumber) btn.classList.add("is-on");
      if (getMark(t.taskNumber)) btn.classList.add("is-flag");
      if (billedNow(cmp)) btn.classList.add("has-bill");
      var priorW = t.budget ? Math.min(100, (cmp.previousCumulativeAmount / t.budget) * 100) : 0;
      var addW = t.budget ? Math.min(100 - priorW, (Math.max(0, cmp.changeAmount) / t.budget) * 100) : 0;
      var shown = state.view === 10 ? cmp.changeAmount : cmp.currentInvoiceAmount;
      btn.innerHTML =
        t.taskNumber +
        '<span class="amt">' + (shown === 0 ? "—" : money(shown)) + "</span>" +
        '<span class="mini"><i style="width:' + priorW + '%"></i><b style="width:' + addW + '%"></b></span>';
      btn.title = t.taskNumber + " " + t.taskName;
      btn.addEventListener("click", function () { select(t.taskNumber, true); });
      host.appendChild(btn);
    });
  }

  function fact(label, value, cls) {
    return '<div class="' + (cls || "") + '"><dt>' + esc(label) + "</dt><dd>" + value + "</dd></div>";
  }

  function renderBar(cmp) {
    var budget = cmp.budget || 0;
    var priorW = budget ? (cmp.previousCumulativeAmount / budget) * 100 : 0;
    var addW = budget ? (Math.max(0, cmp.changeAmount) / budget) * 100 : 0;
    return (
      '<div class="bar" role="img" aria-label="Prior ' + money(cmp.previousCumulativeAmount) +
      ", added " + money(cmp.changeAmount) + ", remaining " + money(cmp.remainingAmount) + '">' +
      '<span class="prior" style="width:' + priorW + '%"></span>' +
      '<span class="add" style="width:' + addW + '%"></span></div>' +
      '<div class="legend">' +
      '<span><i class="sw prior"></i>Already billed through ' + cmp.prevLabel + ": " +
      money(cmp.previousCumulativeAmount) + " (" + cmp.previousPercent + "%)</span>" +
      '<span><i class="sw add"></i>Added on ' + cmp.currLabel + ": " +
      money(cmp.changeAmount) + " (" + (cmp.changePercent >= 0 ? "+" : "") + cmp.changePercent + " pts)</span>" +
      '<span><i class="sw rem"></i>Remaining: ' + money(cmp.remainingAmount) +
      " (" + cmp.remainingPercent + "% of task budget)</span></div>"
    );
  }

  function renderSheet() {
    if (!state.selected) {
      $("empty-sheet").hidden = false;
      $("review").hidden = true;
      return;
    }
    var cmp = compare(state.selected);
    var t = cmp.task;
    $("empty-sheet").hidden = true;
    $("review").hidden = false;
    $("rv-kicker").textContent = "Task " + t.taskNumber;
    $("rv-name").textContent = t.taskName;
    $("rv-meta").textContent = t.stageName + " · budget " + money(cmp.budget) +
      " · billing table p. " + t.invoicePage;
    $("rv-now").textContent = money(cmp.currentInvoiceAmount);
    $("rv-now-sub").textContent = cmp.currLabel + " current billed column. Cumulative is now " +
      money(cmp.currentCumulativeAmount) + " (" + cmp.currentPercent + "% billed).";
    $("rv-change-title").textContent = cmp.independent
      ? "What changed on Invoice 9?"
      : "What changed since Invoice 9?";
    $("rv-facts").innerHTML =
      fact("Task / billing item", t.taskNumber + " · " + esc(t.taskName), "wide") +
      fact("Task budget", money(cmp.budget)) +
      fact(cmp.prevLabel + " cumulative", money(cmp.previousCumulativeAmount) + " · " + cmp.previousPercent + "%") +
      fact(cmp.currLabel + " this invoice", money(cmp.currentInvoiceAmount), "hi") +
      fact(cmp.currLabel + " cumulative", money(cmp.currentCumulativeAmount) + " · " + cmp.currentPercent + "%", "hi") +
      fact("Change", money(cmp.changeAmount) + " · " + (cmp.changePercent >= 0 ? "+" : "") + cmp.changePercent + " pts", "hi") +
      fact("Remaining", money(cmp.remainingAmount) + " · " + cmp.remainingPercent + "%");
    if (cmp.independent) {
      $("rv-facts").innerHTML += fact(
        "Note",
        "Invoice 8 is not in this test. Previous figures are the Prior Billed column printed on Invoice 9.",
        "wide"
      );
    }
    $("rv-bar").innerHTML = renderBar(cmp);

    var msgs = [];
    if (cmp.budgetNote) msgs.push(cmp.budgetNote);
    if (cmp.priorMismatch) {
      msgs.push(cmp.currLabel + " prints prior billed as " + money(cmp.printedPrior) +
        ", which does not match Invoice 9’s ending total of " + money(cmp.previousCumulativeAmount) + ".");
    }
    if (cmp.currentMismatch) {
      msgs.push("The Current Billed column (" + money(cmp.currentInvoiceAmount) +
        ") does not equal the change in cumulative totals (" + money(cmp.changeAmount) + ").");
    }
    $("rv-mismatch").hidden = msgs.length === 0;
    $("rv-mismatch").textContent = msgs.join(" ");

    var evidence = (t.progressEvidence || []).map(function (item) {
      return "<li>" + esc(item) + "</li>";
    }).join("");
    $("rv-why").innerHTML =
      '<div class="why">' +
      (t.rationaleUnclear ? '<p class="unclear">Billing rationale is not clear from the invoice materials.</p>' : "") +
      "<h4>Consultant explanation</h4><p>" + esc(t.consultantNotes) + "</p>" +
      "<h4>Evidence of progress</h4>" +
      (evidence
        ? "<ul>" + evidence + "</ul>"
        : "<p>No dated work product, meeting, trip, or deliverable for this increment is identified on the invoice materials.</p>") +
      "<h4>Reviewer interpretation</h4>" +
      (t.reviewerInterpretation
        ? '<p class="interp">' + esc(t.reviewerInterpretation) + "</p>"
        : "<p>No additional interpretation beyond the invoice text.</p>") +
      (t.statusPage
        ? '<p><button type="button" id="goto-notes">Open related invoice page ' + t.statusPage + "</button></p>"
        : "") +
      "</div>";
    var go = $("goto-notes");
    if (go) {
      go.addEventListener("click", function () {
        state.page = t.statusPage;
        drawPage();
        pageChrome();
      });
    }
    renderMarkForm(t);
    pageChrome();
  }

  function renderMarkForm(t) {
    var mark = getMark(t.taskNumber);
    $("mark-btn").classList.toggle("is-on", !!mark);
    $("mark-btn").textContent = mark ? "Marked for discussion" : "Mark for discussion";
    $("mark-form").hidden = !mark;
    if (mark) {
      $("mark-cat").value = mark.category || "Clarify billing";
      $("mark-text").value = mark.note || "";
      $("mark-status").value = mark.status || "Open";
    }
  }

  function pageChrome() {
    var inv = current();
    $("page-label").textContent = "Page " + state.page + " of " + inv.pageCount;
    var onPage = inv.tasks.filter(function (t) {
      return t.invoicePage === state.page || t.statusPage === state.page;
    }).map(function (t) { return t.taskNumber; });
    var unique = onPage.filter(function (n, i) { return onPage.indexOf(n) === i; });
    $("on-page").textContent = unique.length
      ? "On this page: " + unique.join(", ")
      : "";
  }

  function select(number, jump) {
    state.selected = number;
    var t = task(current(), number);
    if (jump && t) state.page = t.invoicePage;
    renderIndex();
    renderSheet();
    if (jump) drawPage();
  }

  function setView(n) {
    state.view = n;
    $("view-10").setAttribute("aria-pressed", n === 10 ? "true" : "false");
    $("view-9").setAttribute("aria-pressed", n === 9 ? "true" : "false");
    var inv = current();
    $("compare-line").textContent = n === 10
      ? "Compare against: Invoice 9"
      : "Invoice 9 on its own. Prior figures are the Prior Billed column printed on Invoice 9.";
    $("period-line").textContent =
      "Invoice " + inv.invoiceNumber + " · " + inv.invoiceId + " · " + inv.billingPeriod +
      " · this invoice " + money(inv.invoiceTotal) +
      " · cumulative " + money(inv.cumulativeTotal) + " (" + inv.printedPercentComplete + "% billed)";
    state.page = inv.billingTablePage;
    loadPdf();
    if (state.selected && task(inv, state.selected)) select(state.selected, true);
    else select(firstBilled(), true);
  }

  function firstBilled() {
    var hit = current().tasks.find(function (t) {
      return compare(t.taskNumber).currentInvoiceAmount > 0;
    });
    return hit ? hit.taskNumber : current().tasks[0].taskNumber;
  }

  function loadPdf() {
    var inv = current();
    state.pdf = null;
    if (!window.pdfjsLib) {
      $("error").hidden = false;
      $("error").textContent = "PDF.js did not load. Keep python server.py running and refresh.";
      return;
    }
    pdfjsLib.GlobalWorkerOptions.workerSrc = "lib/pdf.worker.min.js";
    pdfjsLib.getDocument(inv.pdf).promise.then(function (doc) {
      if (current().pdf !== inv.pdf) return;
      state.pdf = doc;
      drawPage();
      pageChrome();
    }).catch(function () {
      $("error").hidden = false;
      $("error").textContent = "Could not open " + inv.pdf + ". Run python server.py and open http://127.0.0.1:8770/";
    });
  }

  function drawPage() {
    if (!state.pdf || state.drawing) return;
    var inv = current();
    if (state.page < 1) state.page = 1;
    if (state.page > inv.pageCount) state.page = inv.pageCount;
    state.drawing = true;
    state.pdf.getPage(state.page).then(function (page) {
      var canvas = $("page");
      var stage = $("stage");
      var availableW = Math.max(320, stage.clientWidth - 24);
      var availableH = Math.max(320, stage.clientHeight - 24);
      var base = page.getViewport({ scale: 1 });
      var scale = Math.min(availableW / base.width, availableH / base.height);
      var viewport = page.getViewport({ scale: scale });
      canvas.width = viewport.width;
      canvas.height = viewport.height;
      return page.render({ canvasContext: canvas.getContext("2d"), viewport: viewport }).promise;
    }).then(function () {
      state.drawing = false;
      pageChrome();
    }).catch(function () {
      state.drawing = false;
    });
  }

  function changePage(delta) {
    var next = state.page + delta;
    if (next < 1 || next > current().pageCount) return;
    state.page = next;
    drawPage();
  }

  function pairRow(number) {
    var prev = task(state.inv9, number);
    var curr = task(state.inv10, number);
    return {
      taskNumber: number,
      taskName: curr.taskName,
      previousPercent: prev.printedPercent,
      currentPercent: curr.printedPercent,
      changeAmount: round2(curr.totalBilled - prev.totalBilled),
      currentInvoiceAmount: curr.currentInvoiceAmount,
      priorMismatch: Math.abs(curr.printedPriorBilled - prev.totalBilled) > 0.02
    };
  }

  function renderSummary() {
    var a = state.inv9;
    var b = state.inv10;
    var rows = b.tasks.map(function (t) { return pairRow(t.taskNumber); });
    var increased = rows.filter(function (r) { return r.changeAmount > 0; })
      .sort(function (x, y) { return y.changeAmount - x.changeAmount; });
    var unchanged = rows.filter(function (r) {
      return r.changeAmount === 0 && !r.priorMismatch && r.currentInvoiceAmount === 0;
    });
    var near = rows.filter(function (r) { return r.currentPercent >= 90; });
    var flagged = Object.keys(state.notes.items).length;
    $("summary-body").innerHTML =
      '<dl class="sum">' +
      "<div><dt>Invoice 9 billed this period</dt><dd>" + money(a.invoiceTotal) + "</dd></div>" +
      "<div><dt>Invoice 10 billed this period</dt><dd>" + money(b.invoiceTotal) + "</dd></div>" +
      "<div><dt>Invoice 9 cumulative</dt><dd>" + money(a.cumulativeTotal) + " · " + a.printedPercentComplete + "%</dd></div>" +
      "<div><dt>Invoice 10 cumulative</dt><dd>" + money(b.cumulativeTotal) + " · " + b.printedPercentComplete + "%</dd></div>" +
      "<div><dt>Overall increase</dt><dd>" + money(round2(b.cumulativeTotal - a.cumulativeTotal)) + "</dd></div>" +
      "<div><dt>Marked for discussion</dt><dd>" + flagged + "</dd></div></dl>" +
      "<h3>Largest increases</h3>" +
      increased.slice(0, 6).map(function (r) {
        return '<button type="button" class="jump" data-task="' + r.taskNumber + '"><strong>' +
          r.taskNumber + " " + esc(r.taskName) + "</strong><span>" + money(r.changeAmount) +
          " · " + r.previousPercent + "% → " + r.currentPercent + "%</span></button>";
      }).join("") +
      "<h3>No billing change</h3><p>" + unchanged.map(function (r) { return r.taskNumber; }).join(", ") + "</p>" +
      "<h3>At or near 100% billed</h3><p>" +
      near.map(function (r) { return r.taskNumber + " (" + r.currentPercent + "%)"; }).join(", ") + "</p>";
  }

  function renderDisc() {
    var items = Object.keys(state.notes.items).map(function (k) { return state.notes.items[k]; });
    if (!items.length) {
      $("disc-body").innerHTML = "<p>No tasks marked.</p>";
      return;
    }
    $("disc-body").innerHTML = items.map(function (item) {
      return '<button type="button" class="jump" data-view="' + item.invoiceNumber +
        '" data-task="' + esc(item.taskNumber) + '"><strong>' +
        esc(item.taskNumber) + " · " + esc(item.taskName) + "</strong><span>" +
        esc(item.category || "") + " · Invoice " + item.invoiceNumber + " p. " +
        (item.invoicePage || "?") + " · " + esc(item.status || "Open") + "</span><span>" +
        esc(item.note || "") + "</span></button>";
    }).join("");
  }

  function bind() {
    $("view-10").addEventListener("click", function () { setView(10); });
    $("view-9").addEventListener("click", function () { setView(9); });
    $("prev-page").addEventListener("click", function () { changePage(-1); });
    $("next-page").addEventListener("click", function () { changePage(1); });
    $("mark-btn").addEventListener("click", function () {
      if (!state.selected || getMark(state.selected)) return;
      setMark(state.selected, { category: "Clarify billing", note: "", status: "Open" });
      renderSheet();
      renderIndex();
    });
    $("unmark-btn").addEventListener("click", function () {
      if (!state.selected) return;
      setMark(state.selected, null);
      renderSheet();
      renderIndex();
    });
    ["mark-cat", "mark-text", "mark-status"].forEach(function (id) {
      $(id).addEventListener("input", saveMark);
      $(id).addEventListener("change", saveMark);
    });
    $("open-summary").addEventListener("click", function () {
      renderSummary();
      $("summary-panel").hidden = false;
    });
    $("close-summary").addEventListener("click", function () { $("summary-panel").hidden = true; });
    $("open-disc").addEventListener("click", function () {
      renderDisc();
      $("disc-panel").hidden = false;
    });
    $("close-disc").addEventListener("click", function () { $("disc-panel").hidden = true; });
    $("summary-body").addEventListener("click", function (ev) {
      var btn = ev.target.closest("[data-task]");
      if (!btn) return;
      $("summary-panel").hidden = true;
      setView(10);
      select(btn.getAttribute("data-task"), true);
    });
    $("disc-body").addEventListener("click", function (ev) {
      var btn = ev.target.closest("[data-task]");
      if (!btn) return;
      $("disc-panel").hidden = true;
      setView(Number(btn.getAttribute("data-view")));
      select(btn.getAttribute("data-task"), true);
    });
    $("export-notes").addEventListener("click", function () {
      var blob = new Blob([JSON.stringify({
        project: "ʻEwa Development Plan",
        tool: "invoice-9-10-review",
        savedAt: new Date().toISOString(),
        items: state.notes.items
      }, null, 2)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "ewa-dp-invoice-9-10-notes.json";
      a.click();
      URL.revokeObjectURL(a.href);
    });
    $("import-notes").addEventListener("change", function (ev) {
      var file = ev.target.files && ev.target.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function () {
        try {
          var parsed = JSON.parse(reader.result);
          if (!parsed.items) throw new Error("no items");
          state.notes = { items: parsed.items };
          saveNotes();
          renderIndex();
          renderSheet();
        } catch (err) {
          $("error").hidden = false;
          $("error").textContent = "Could not import that JSON file.";
        }
      };
      reader.readAsText(file);
      ev.target.value = "";
    });
    $("clear-notes").addEventListener("click", function () {
      if (!confirm("Clear reviewer marks stored in this browser?")) return;
      state.notes = { items: {} };
      saveNotes();
      renderIndex();
      renderSheet();
    });
    window.addEventListener("resize", function () {
      clearTimeout(bind.resize);
      bind.resize = setTimeout(drawPage, 150);
    });
  }

  function saveMark() {
    if (!state.selected || !getMark(state.selected)) return;
    setMark(state.selected, {
      category: $("mark-cat").value,
      note: $("mark-text").value,
      status: $("mark-status").value
    });
    renderIndex();
  }

  Promise.all([
    fetch("data/invoice9.json").then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }),
    fetch("data/invoice10.json").then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
  ]).then(function (pair) {
    state.inv9 = pair[0];
    state.inv10 = pair[1];
    $("disc-count").textContent = String(Object.keys(state.notes.items).length);
    bind();
    setView(10);
  }).catch(function () {
    $("error").hidden = false;
    $("error").textContent = "Could not load invoice data. From this folder run python server.py, then open http://127.0.0.1:8770/";
  });
})();
