"""Build invoice9.json and invoice10.json from printed invoice figures."""
import json
from pathlib import Path

TASK_META = {
    "1.1": {"taskName": "Project Workplan and Overall Schedule", "stage": "1", "stageName": "Project Initiation and Existing Conditions"},
    "1.2": {"taskName": "Team Kick-Off Meeting", "stage": "1", "stageName": "Project Initiation and Existing Conditions"},
    "1.3": {"taskName": "Data Collection and Base Map", "stage": "1", "stageName": "Project Initiation and Existing Conditions"},
    "1.4": {"taskName": "Growth Projections", "stage": "1", "stageName": "Project Initiation and Existing Conditions"},
    "1.5": {"taskName": "Topic-Specific Fact Sheets & Technical Background Memos", "stage": "1", "stageName": "Project Initiation and Existing Conditions"},
    "2.1": {"taskName": "Project Management and Meetings/Trips", "stage": "2", "stageName": "Meetings and Collaboration"},
    "2.2": {"taskName": "Agency Meetings and Coordination", "stage": "2", "stageName": "Meetings and Collaboration"},
    "3.1": {"taskName": "Engagement Strategy Memo", "stage": "3", "stageName": "Community Engagement"},
    "3.2": {"taskName": "Branding/Identity", "stage": "3", "stageName": "Community Engagement"},
    "3.3": {"taskName": "Project Fact Sheet", "stage": "3", "stageName": "Community Engagement"},
    "3.4": {"taskName": "Project Website", "stage": "3", "stageName": "Community Engagement"},
    "3.5": {"taskName": "Neighborhood Profiles", "stage": "3", "stageName": "Community Engagement"},
    "3.6": {"taskName": "Stakeholder Meetings (x36)", "stage": "3", "stageName": "Community Engagement"},
    "3.7": {"taskName": "Community Advisory Committee (x8)", "stage": "3", "stageName": "Community Engagement"},
    "3.8": {"taskName": "Community Symposium", "stage": "3", "stageName": "Community Engagement"},
    "3.9": {"taskName": "Focus Groups (x6)", "stage": "3", "stageName": "Community Engagement"},
    "3.10": {"taskName": "Pop-Ups (x2 rounds)", "stage": "3", "stageName": "Community Engagement"},
    "3.11": {"taskName": "Draft Plan Open House", "stage": "3", "stageName": "Community Engagement"},
    "3.12": {"taskName": "Online Surveys and Feedback (x2 rounds)", "stage": "3", "stageName": "Community Engagement"},
    "4.1": {"taskName": "Vision Statement and Key Elements/Goals", "stage": "4", "stageName": "Growth Framework"},
    "4.2": {"taskName": "Revised Place Types", "stage": "4", "stageName": "Growth Framework"},
    "4.3": {"taskName": "Draft Conceptual Maps", "stage": "4", "stageName": "Growth Framework"},
    "4.4": {"taskName": "Future Growth Concepts (for Areas of Change)", "stage": "4", "stageName": "Growth Framework"},
    "5.1": {"taskName": "Plan Outline and Format", "stage": "5", "stageName": "Draft Development Plan"},
    "5.2": {"taskName": "Draft Policies, Actions, Frameworks, and Metrics", "stage": "5", "stageName": "Draft Development Plan"},
    "6.1": {"taskName": "Administrative Draft Development Plan", "stage": "6", "stageName": "Updated Development Plan"},
    "6.2": {"taskName": "Screencheck Draft Development Plan", "stage": "6", "stageName": "Updated Development Plan"},
    "6.3": {"taskName": "Public Review Draft Development Plan", "stage": "6", "stageName": "Updated Development Plan"},
    "6.4": {"taskName": "Proposed Plan", "stage": "6", "stageName": "Updated Development Plan"},
    "GET": {"taskName": "General Excise Tax", "stage": "other", "stageName": "Tax, reimbursables, and contingency"},
    "REIMB": {"taskName": "Reimbursables", "stage": "other", "stageName": "Tax, reimbursables, and contingency"},
    "CONT": {"taskName": "Extra Work/Contingency", "stage": "other", "stageName": "Tax, reimbursables, and contingency"},
}

# Printed invoice columns: budget, percent, total, remaining, prior, current
INV9_LINES = {
    "1.1": (4566, 29, 1308.75, 3257.25, 1308.75, 0),
    "1.2": (12252, 72, 8793.45, 3458.55, 8675.06, 118.39),
    "1.3": (6348, 85, 5422.65, 925.35, 3979.19, 1443.46),
    "1.4": (3010, 99, 2992.50, 17.50, 742.50, 2250.00),
    "1.5": (55770, 70, 39158.23, 16611.77, 34036.98, 5121.25),
    "2.1": (70567, 77, 54399.04, 16167.96, 52066.54, 2332.50),
    "2.2": (18784, 43, 8046.70, 10737.30, 7877.95, 168.75),
    "3.1": (5601, 29, 1616.25, 3984.75, 1376.25, 240.00),
    "3.2": (3490, 99, 3463.75, 26.25, 3463.75, 0),
    "3.3": (4830, 95, 4591.25, 238.75, 1777.50, 2813.75),
    "3.4": (11170, 97, 10876.25, 293.75, 10836.25, 40.00),
    "3.5": (4980, 99, 4950.00, 30.00, 4781.25, 168.75),
    "3.6": (23374, 8, 1901.25, 21472.75, 1901.25, 0),
    "3.7": (43878, 0, 210.00, 43668.00, 210.00, 0),
    "3.8": (15966, 0, 0, 15966.00, 0, 0),
    "3.9": (13876, 0, 0, 13876.00, 0, 0),
    "3.10": (14834, 0, 0, 14834.00, 0, 0),
    "3.11": (13053, 0, 0, 13053.00, 0, 0),
    "3.12": (7283, 0, 0, 7283.00, 0, 0),
    "4.1": (4210, 0, 0, 4210.00, 0, 0),
    "4.2": (6050, 0, 0, 6050.00, 0, 0),
    "4.3": (9917, 0, 0, 9917.00, 0, 0),
    "4.4": (8590, 0, 0, 8590.00, 0, 0),
    "5.1": (3231, 70, 2248.75, 982.25, 2248.75, 0),
    "5.2": (41672, 0, 0, 41672.00, 0, 0),
    "6.1": (79256, 0, 0, 79256.00, 0, 0),
    "6.2": (35145, 0, 0, 35145.00, 0, 0),
    "6.3": (9240, 0, 0, 9240.00, 0, 0),
    "6.4": (13877, 0, 0, 13877.00, 0, 0),
    "GET": (25672, 28, 7171.47, 18500.53, 6462.52, 708.95),
    "REIMB": (9500, 3, 250.90, 9249.10, 250.90, 0),
    "CONT": (10000, 20, 1966.25, 8033.75, 1617.50, 348.75),
}

INV10_LINES = {
    "1.1": (4566, 49, 2249.74, 2316.26, 2249.74, 0),
    "1.2": (12252, 100, 12223.45, 28.55, 7852.45, 4371.00),
    "1.3": (6348, 98, 6226.65, 121.35, 5422.65, 804.00),
    "1.4": (3010, 99, 2992.50, 17.50, 2992.50, 0),
    "1.5": (55769, 87, 48634.93, 7134.07, 39158.23, 9476.70),
    "2.1": (70567, 82, 57744.04, 12822.46, 53874.04, 3345.00),
    "2.2": (18784, 50, 9306.70, 9476.80, 8046.70, 1260.00),
    "3.1": (5602, 71, 3966.90, 1635.10, 1616.25, 2350.65),
    "3.2": (3490, 99, 3463.75, 26.25, 3463.75, 0),
    "3.3": (4830, 95, 4591.25, 238.75, 4591.25, 0),
    "3.4": (11170, 97, 10876.25, 293.75, 10876.25, 0),
    "3.5": (4980, 99, 4950.00, 30.00, 4950.00, 0),
    "3.6": (23375, 24, 5576.25, 17798.25, 1901.25, 3675.00),
    "3.7": (43879, 0, 210.00, 43668.50, 210.00, 0),
    "3.8": (15966, 0, 0, 15966.00, 0, 0),
    "3.9": (13876, 0, 0, 13876.00, 0, 0),
    "3.10": (14834, 0, 0, 14834.00, 0, 0),
    "3.11": (13053, 0, 0, 13053.00, 0, 0),
    "3.12": (7283, 0, 0, 7283.00, 0, 0),
    "4.1": (4210, 0, 0, 4210.00, 0, 0),
    "4.2": (7107, 0, 0, 7107.00, 0, 0),
    "4.3": (8860, 0, 0, 8860.00, 0, 0),
    "4.4": (8590, 0, 0, 8590.00, 0, 0),
    "5.1": (3231, 70, 2248.75, 982.25, 2248.75, 0),
    "5.2": (41672, 0, 0, 41672.00, 0, 0),
    "6.1": (79256, 0, 0, 79256.00, 0, 0),
    "6.2": (35146, 0, 0, 35146.00, 0, 0),
    "6.3": (9240, 0, 0, 9240.00, 0, 0),
    "6.4": (13876, 0, 0, 13876.00, 0, 0),
    "GET": (25672, 35, 9091.70, 16580.30, 7171.47, 1920.23),
    "REIMB": (9500, 4, 378.27, 9121.73, 250.90, 127.37),
    "CONT": (10000, 20, 1966.25, 8033.75, 1966.25, 0),
}

# Invoice 10 packet: p1-2 letter, p3-8 Attachment 1, p9 billing table
INV10_PAGES = {
    "billing": 9,
    "letter": [1, 2],
    "statusByTask": {
        "1.1": 3, "1.2": 3, "1.3": 3, "1.4": 4, "1.5": 4,
        "2.1": 5, "2.2": 5,
        "3.1": 5, "3.2": 6, "3.3": 6, "3.4": 6, "3.5": 7, "3.6": 7,
        "3.7": 7, "3.8": 7, "3.9": 7, "3.10": 7, "3.11": 7, "3.12": 7,
        "4.1": 8, "4.2": 8, "4.3": 8, "4.4": 8,
        "5.1": 8, "5.2": 8,
        "6.1": 8, "6.2": 8, "6.3": 8, "6.4": 8,
        "GET": 2, "REIMB": 2, "CONT": 2,
    },
}

# Invoice 9 packet: p1 billing table (text-extractable). Remaining pages are the
# cover memorandum / status report in the same PDF (9 pages total).
INV9_PAGES = {
    "billing": 1,
    "letter": [2, 3],
    "statusByTask": {},
}

INV9_NOTES = {
    "1.1": {
        "consultantNotes": "Invoice 9 does not describe work on the project workplan during May 1–22, 2026. No amount is billed on this line this period.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "1.2": {
        "consultantNotes": "Invoice 9 bills $118.39 to Team Kick-Off Meeting. The invoice materials reviewed for this prototype do not describe kickoff-meeting work during May 1–22, 2026. Kickoff meetings are dated October 28–30, 2025, in later status tables.",
        "progressEvidence": [],
        "rationaleUnclear": True,
        "reviewerInterpretation": "A small residual charge appears on a task whose meetings occurred in October 2025. The May invoice does not explain the $118.39.",
    },
    "1.3": {
        "consultantNotes": "The City payment memo for Invoice 9 (summarizing the consultant status report) says the consultant coordinated with DPP and HoLIS to obtain residential pipeline project data. The consultant cover notes extracted for Invoice 9 also state that 1.75 April hours on Task 1.3 were missed on Invoice 8 and are billed on Invoice 9 to contingency, not to this line.",
        "progressEvidence": [
            "Coordination with DPP and HoLIS on residential pipeline project data (City memo summary of the status report)",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The $1,443.46 on this line is not the 1.75 missed April hours (those were sent to contingency). The invoice table does not break out what portion of $1,443.46 is pipeline-data work versus other Task 1.3 effort.",
    },
    "1.4": {
        "consultantNotes": "The City payment memo says updated growth-projection information was integrated into the land-use technical memorandum. Invoice 9 bills $2,250.00 and prints 99% complete. Later Invoice 10 status text says growth-projection data were summarized and included in Task 1.5 memos.",
        "progressEvidence": [
            "Updated growth projection information integrated into the land-use technical memorandum (City memo summary)",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The line moves from 25% printed complete on the prior billed column ($742.50) to 99% ($2,992.50). The invoice does not say the standalone growth-projections deliverable was newly completed this period; it describes integration into the land-use memo.",
    },
    "1.5": {
        "consultantNotes": "Largest Invoice 9 task charge ($5,121.25). City memo: work continued on technical memoranda for land use, infrastructure, sustainability, and healthy communities, including subconsultant coordination and review of plans, policies, and background information. Consultant note extracted from the Invoice 9 status report: Task 1.5 needed more effort than scoped; some extra time was billed to Task 3.3 (fact sheet), which was already complete and under budget.",
        "progressEvidence": [
            "Continued technical memorandum work (land use, infrastructure, sustainability, healthy communities)",
            "Subconsultant coordination and background-plan review",
            "Consultant statement that some extra Task 1.5 effort was charged to Task 3.3",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The invoice supports ongoing memo work. It does not itemize which memos advanced during May 1–22, and it states that some 1.5 effort was placed on the already-finished fact-sheet line.",
    },
    "2.1": {
        "consultantNotes": "City memo: regular project management, subconsultant coordination, bi-monthly communication with DPP, project updates, invoicing, and coordination on the proposed contract amendment.",
        "progressEvidence": [
            "Subconsultant coordination",
            "Bi-monthly DPP communication / project updates / invoicing",
            "Contract-amendment coordination",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The $2,332.50 is described as ongoing management. The invoice does not list a working trip during May 1–22.",
    },
    "2.2": {
        "consultantNotes": "City memo: the consultant reviewed agency meeting notes and incorporated key takeaways into ongoing technical work. Invoice 9 bills $168.75. No new agency meeting during this period is named in the materials reviewed for this prototype.",
        "progressEvidence": [
            "Review of agency meeting notes; takeaways incorporated into technical work (City memo summary)",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "This appears to be follow-up on earlier agency meetings rather than a new meeting this period. The invoice does not say how many notes were reviewed.",
    },
    "3.1": {
        "consultantNotes": "City memo: reviewing and refining the public engagement strategy. Consultant note extracted from the Invoice 9 status report: extra Task 3.1 hours are being held for Task 3.1A after the contract amendment. Invoice 9 still bills $240.00 on this line (29% printed complete).",
        "progressEvidence": [
            "Review/refinement of the public engagement strategy (City memo summary)",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The consultant said extra 3.1 hours would be held, yet $240.00 was billed. The invoice does not show a draft memo submitted in this period (Invoice 10 later dates the draft to June 9, 2026).",
    },
    "3.2": {
        "consultantNotes": "No Invoice 9 current billing. Branding remains at 99% / $3,463.75.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "3.3": {
        "consultantNotes": "Invoice 9 bills $2,813.75 and prints 95% complete. Consultant note extracted from the Invoice 9 status report: Task 1.5 needed more effort than scoped; some extra time was billed to Task 3.3 because the fact sheet was already complete and under budget. Later status tables date the final fact sheet to January 14, 2026.",
        "progressEvidence": [
            "Consultant statement that Task 3.3 was used for overflow Task 1.5 time",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The charge is explained as a coding/overflow choice, not as new fact-sheet work in May. Percent billed moved from 37% to 95% on a deliverable dated January 14.",
    },
    "3.4": {
        "consultantNotes": "Invoice 9 bills $40.00. City memo: continuing development of the project website and public contact intake form. Consultant note extracted from the Invoice 9 status report: Task 3.4 budget is depleted.",
        "progressEvidence": [
            "Website and public contact intake form work (City memo summary)",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "A $40 residual charge appears on a line the consultant already described as depleted (97% printed complete).",
    },
    "3.5": {
        "consultantNotes": "City memo: updating neighborhood profile layouts based on DPP comments; compiling neighborhood-scale data and maps; coordinating with HoLIS on network analysis mapping. Invoice 9 bills $168.75 and prints 99% complete.",
        "progressEvidence": [
            "Neighborhood profile layout updates from DPP comments",
            "Neighborhood-scale data and maps",
            "HoLIS network-analysis mapping coordination",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The period notes support profile/map work. Draft profiles are dated June 10 and 17 on Invoice 10, after this billing period. The line is already at 99%.",
    },
    "3.6": {
        "consultantNotes": "No Invoice 9 current billing. Line remains at 8% / $1,901.25.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "3.7": {
        "consultantNotes": "No Invoice 9 current billing. $210 remains on the line with 0% printed complete.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "GET": {
        "consultantNotes": "General excise tax of $708.95 is printed on Invoice 9, moving GET from $6,462.52 to $7,171.47 (28%).",
        "progressEvidence": ["GET line on the Invoice 9 billing table"],
        "rationaleUnclear": False,
        "reviewerInterpretation": "Tax follows billed services. No separate work product.",
    },
    "REIMB": {
        "consultantNotes": "No reimbursable charge on Invoice 9. Line remains $250.90 (3%).",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "CONT": {
        "consultantNotes": "Invoice 9 bills $348.75 to Extra Work/Contingency (20% printed complete, $1,966.25 total). Consultant note extracted from the Invoice 9 status report: 1.75 April hours on Task 1.3 were missed on Invoice 8 and are billed here to contingency. The City payment memo states DPP and the consultant discussed the Invoice 9 notes on July 14, 2026, and agreed to scrutinize future billings, emphasize deliverable-based billing, and use contingency more carefully.",
        "progressEvidence": [
            "Consultant statement that 1.75 missed April Task 1.3 hours were billed to contingency",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The invoice attributes this increment to missed April hours, not new May extra work. The dollar amount is not shown as 1.75 × a stated rate on the billing table.",
    },
}

INV10_NOTES = {
    "1.1": {
        "consultantNotes": "Invoice 10 prints $0.00 current billed, but total billed rises from Invoice 9’s $1,308.75 (29%) to $2,249.74 (49%). The printed prior on Invoice 10 is $2,249.74, which does not match Invoice 9’s ending total. Attachment 1 still says the workplan is ongoing and will be aligned with the engagement strategy.",
        "progressEvidence": [],
        "rationaleUnclear": True,
        "reviewerInterpretation": "The cumulative balance increased without a current-period charge. That is a table discrepancy, not documented May 23–June 30 workplan work.",
    },
    "1.2": {
        "consultantNotes": "Invoice 10 bills $4,371.00 and prints 100% complete ($12,223.45 total). The May 23–June 30 status letter does not mention kickoff-meeting work. Attachment 1 dates kickoff to October 28–30, 2025, and notes to November 8, 2025, and marks the task Completed. Invoice 10’s printed prior ($7,852.45) does not match Invoice 9’s ending total ($8,793.45).",
        "progressEvidence": [],
        "rationaleUnclear": True,
        "reviewerInterpretation": "A large charge lands on a task Attachment 1 calls completed in 2025. The letter’s “tasks completed this time period” list does not include Task 1.2.",
    },
    "1.3": {
        "consultantNotes": "Invoice 10 bills $804.00 (98% / $6,226.65). The status letter lists Task 1.3 among tasks that have exceeded the task budget, due in part to work described as outside of scope. Attachment 1: base map completed December 30, 2025; status “Completed (pending sub invoicing)”; AGOL/HoLIS collaboration (including March 23, 2026 meeting) is described as ongoing setup, not as a June deliverable.",
        "progressEvidence": [
            "Consultant statement that Task 1.3 has exceeded budget, in part for out-of-scope work",
            "Attachment 1: base map dated December 30, 2025; pending sub invoicing",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The $804 looks like continued or late invoicing on a December 2025 base map / AGOL setup, not a new May–June map. The letter does not itemize the $804.",
    },
    "1.4": {
        "consultantNotes": "No Invoice 10 current billing. Line stays at 99% / $2,992.50. Attachment 1 marks Growth Projections Completed and says data were summarized into Task 1.5 memos.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "1.5": {
        "consultantNotes": "Largest Invoice 10 task charge ($9,476.70; 87% / $48,634.93). Letter: completed technical memos for land use, infrastructure, sustainability, and healthy communities and submitted them to DPP on June 16, 2026; coordinated with subconsultants on other memos and submitted those drafts the same day; began a matrix of key findings in anticipation of a budget adjustment. Attachment 1: outlines January 29, 2026; draft memos (land use, infrastructure, sustainability, healthy communities, plus circulation, cultural/historic, parks and open space from subs) submitted 6/16/26. Letter also lists Task 1.5 as over the task budget, in part for out-of-scope work.",
        "progressEvidence": [
            "Draft technical memos submitted June 16, 2026 (land use, infrastructure, sustainability, healthy communities)",
            "Subconsultant draft memos submitted June 16, 2026 (circulation, cultural/historic, parks and open space)",
            "Matrix of key findings started in anticipation of a budget adjustment",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "June 16 draft-memo submittal is the clearest Invoice 10 work product. The letter does not allocate the $9,476.70 among memos versus the findings matrix versus out-of-scope effort.",
    },
    "2.1": {
        "consultantNotes": "Invoice 10 bills $3,345.00 (82% / $57,744.04). Letter: subconsultant coordination and invoicing; regular email with DPP; bimonthly project updates; staff-time allocation; monthly invoice and progress report; coordination on contract reassignment and amendment, vendor portal, and certificate of insurance. Attachment 1 lists June 30, 2026, among bimonthly meetings. Invoice 10’s printed prior ($53,874.04) does not match Invoice 9’s ending total ($54,399.04); printed current plus Invoice 9’s ending total does equal Invoice 10’s total.",
        "progressEvidence": [
            "Bimonthly update dated June 30, 2026 on Attachment 1",
            "Invoice and progress report for this period",
            "Contract reassignment/amendment, vendor portal, and insurance coordination",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The letter supports ongoing management. It does not list a working trip in this period. 82% of the PM/meetings/trips budget is billed while Stages 4–6 remain unbilled.",
    },
    "2.2": {
        "consultantNotes": "Invoice 10 bills $1,260.00 (50% / $9,306.70). The status letter’s “tasks completed this time period” list does not mention agency meetings. Attachment 1 lists in-person agency meetings in October 2025 and additional meetings from December 2025–January 2026, with notes on SharePoint.",
        "progressEvidence": [],
        "rationaleUnclear": True,
        "reviewerInterpretation": "No May 23–June 30 agency meeting is named. The $1,260 is not tied to a dated meeting or notes packet in the Invoice 10 letter.",
    },
    "3.1": {
        "consultantNotes": "Invoice 10 bills $2,350.65 (71% / $3,966.90). Letter: collaborated extensively on the engagement strategy with Keith Mattson, who is primarily responsible for this task. Attachment 1: draft strategy memo prepared by KM, with R+A support, submitted June 9, 2026. Letter lists Task 3.1 among tasks that have exceeded the task budget, in part for out-of-scope work. Printed percent is 71% of a $5,602 budget ($3,966.90 billed), so the printed “exceeded” statement does not match the remaining $1,635.10 on the table.",
        "progressEvidence": [
            "Draft engagement strategy memo submitted June 9, 2026",
            "Collaboration with Keith Mattson described in the status letter",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The June 9 draft is identifiable progress. Whether $2,350.65 is proportionate, and why the letter says the task exceeded budget at 71% billed, is not explained on the invoice.",
    },
    "3.2": {
        "consultantNotes": "No Invoice 10 current billing. Attachment 1: final branding package December 10, 2025; Completed.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "3.3": {
        "consultantNotes": "No Invoice 10 current billing. Attachment 1: final fact sheet January 14, 2026; Completed (pending sub invoicing).",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "3.4": {
        "consultantNotes": "No Invoice 10 current billing (97% / $10,876.25). Letter lists Task 3.4 among tasks that have exceeded the task budget, in part for out-of-scope work. Attachment 1: Completed (pending sub invoicing); website questionnaire/mockup December 17, 2025, and later DPP edits.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "No new website charge this invoice. The “exceeded budget” note is not reflected as a current 3.4 charge; extra website time may have been placed on other lines on earlier invoices.",
    },
    "3.5": {
        "consultantNotes": "Invoice 10 prints $0.00 current billed and leaves the line at 99% / $4,950.00. The same letter describes substantial profile work this period: drafts including an additional ʻEwa profile; HoLIS maps for transit and parks/open space access; drafts submitted June 10, 2026, and revised drafts June 17, 2026. Letter also lists Task 3.5 as over budget, in part for out-of-scope work (the extra ʻEwa profile).",
        "progressEvidence": [
            "Draft neighborhood profiles submitted June 10, 2026",
            "Revised drafts submitted June 17, 2026",
            "Additional ʻEwa DP area profile",
            "HoLIS access-to-transit and parks/open-space analysis maps",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The work products are dated in this period, but Invoice 10 does not charge Task 3.5. The invoice does not say which other line absorbed that effort.",
    },
    "3.6": {
        "consultantNotes": "Invoice 10 bills $3,675.00 (24% / $5,576.25). This task is not in the letter’s “tasks completed this time period” list. Attachment 1: “Initial set of stakeholder calls conducted by DPP and Keith Mattson. Notes summarized on SharePoint.” No call dates in May 23–June 30 are given, and no interview-summary deliverable is dated.",
        "progressEvidence": [
            "Attachment 1 statement that an initial set of stakeholder calls was conducted by DPP and Keith Mattson, with notes on SharePoint",
        ],
        "rationaleUnclear": True,
        "reviewerInterpretation": "The $3,675 is a large new charge. The invoice does not say how many of the 36 meetings occurred, when they occurred, or what notes were produced this period.",
    },
    "3.7": {
        "consultantNotes": "No Invoice 10 current billing. Attachment 1: Not started. $210 remains on the line with 0% printed complete.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
    "GET": {
        "consultantNotes": "Invoice 10 bills $1,920.23 GET (35% / $9,091.70). Letter: previous Fehr & Peers invoices mistakenly included GET inside work-task billing; that will be corrected the next time an invoice is received from Fehr & Peers.",
        "progressEvidence": [
            "GET line on the Invoice 10 billing table",
            "Consultant note that Fehr & Peers GET was previously coded into task lines and will be corrected on a future Fehr invoice",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "GET should track billed services. The Fehr coding error means some prior task totals may include tax. The invoice does not show the correction on this invoice.",
    },
    "REIMB": {
        "consultantNotes": "Invoice 10 bills $127.37. Letter: the direct expense was to mail the executed contract reassignment to DPP because the County does not permit electronic signatures.",
        "progressEvidence": [
            "Mailing of the executed contract reassignment (consultant letter)",
        ],
        "rationaleUnclear": False,
        "reviewerInterpretation": "The letter ties this reimbursable to a specific mailing. No receipt is quoted in the extracted invoice text.",
    },
    "CONT": {
        "consultantNotes": "No Invoice 10 current billing. Contingency stays at 20% / $1,966.25.",
        "progressEvidence": [],
        "rationaleUnclear": False,
        "reviewerInterpretation": "",
    },
}

BLANK_NOTE = {
    "consultantNotes": "No current-period charge and no period-specific explanation on this invoice.",
    "progressEvidence": [],
    "rationaleUnclear": False,
    "reviewerInterpretation": "",
}

CONTRACT_BUDGET_NOTES_10 = {
    "4.2": "Invoice 10 prints this task budget as $7,107. Invoice 9 printed $6,050. Stage 4 total remains $28,767.",
    "4.3": "Invoice 10 prints this task budget as $8,860. Invoice 9 printed $9,917. Stage 4 total remains $28,767.",
}


def money(x):
    return round(float(x), 2)


def task_record(number, printed, notes, invoice_page, status_page, extra=None):
    budget, pct, total, remaining, prior, current = printed
    meta = TASK_META[number]
    rec = {
        "taskNumber": number,
        "taskName": meta["taskName"],
        "stage": meta["stage"],
        "stageName": meta["stageName"],
        "budget": money(budget),
        "printedPercent": pct,
        "totalBilled": money(total),
        "remainingAmount": money(remaining),
        "printedPriorBilled": money(prior),
        "currentInvoiceAmount": money(current),
        "consultantNotes": notes["consultantNotes"],
        "progressEvidence": notes["progressEvidence"],
        "rationaleUnclear": notes["rationaleUnclear"],
        "reviewerInterpretation": notes["reviewerInterpretation"],
        "invoicePage": invoice_page,
        "statusPage": status_page,
    }
    if extra:
        rec.update(extra)
    return rec


def build(invoice_number, header, lines, notes_map, pages):
    tasks = []
    for number, printed in lines.items():
        notes = notes_map.get(number, BLANK_NOTE)
        extra = {}
        if invoice_number == 10 and number in CONTRACT_BUDGET_NOTES_10:
            extra["budgetNote"] = CONTRACT_BUDGET_NOTES_10[number]
        tasks.append(
            task_record(
                number,
                printed,
                notes,
                pages["billing"],
                pages["statusByTask"].get(number, pages["letter"][0] if pages["letter"] else pages["billing"]),
                extra,
            )
        )
    return {
        **header,
        "pageCount": 9,
        "billingTablePage": pages["billing"],
        "letterPages": pages["letter"],
        "tasks": tasks,
    }


inv9 = build(
    9,
    {
        "invoiceNumber": 9,
        "invoiceId": "304.RA24020.001-003",
        "consultant": "Alta Planning + Design, Inc.",
        "projectName": "ʻEwa Development Plan",
        "projectNumber": "304.RA24020.001",
        "invoiceDate": "2026-05-22",
        "billingPeriod": "5/1/2026 to 5/22/2026",
        "periodStart": "2026-05-01",
        "periodEnd": "2026-05-22",
        "invoiceTotal": 15754.55,
        "cumulativeTotal": 159367.44,
        "priorCumulativeTotal": 143612.89,
        "remainingTotal": 430624.56,
        "printedPercentComplete": 27,
        "contractAmount": 589992,
        "pdf": "pdf/invoice9.pdf",
        "sourceFile": "304.RA24020.001-3.pdf",
        "firmsOnInvoice": [
            "Raimi + Associates, an Alta Company",
            "Fehr and Peers, Inc.",
        ],
        "packetNotes": [
            "Billing table is page 1 of the Invoice 9 PDF.",
            "The PDF also includes the consultant cover memorandum and May 1–22 project status report.",
            "A City payment memo dated August 24, 2026, summarizes that status report; consultant-attributed statements below are taken from that memo and from notes extracted from the Invoice 9 status report.",
        ],
    },
    INV9_LINES,
    INV9_NOTES,
    INV9_PAGES,
)

inv10 = build(
    10,
    {
        "invoiceNumber": 10,
        "invoiceId": "304.RA24020.001-004",
        "consultant": "Alta Planning + Design, Inc.",
        "projectName": "ʻEwa Development Plan",
        "projectNumber": "304.RA24020.001",
        "invoiceDate": "2026-08-17",
        "billingPeriod": "5/23/2026 to 6/30/2026",
        "periodStart": "2026-05-23",
        "periodEnd": "2026-06-30",
        "invoiceTotal": 27329.95,
        "cumulativeTotal": 186697.38,
        "priorCumulativeTotal": 159367.44,
        "remainingTotal": 403294.62,
        "printedPercentComplete": 32,
        "contractAmount": 589992,
        "pdf": "pdf/invoice10.pdf",
        "sourceFile": "Invoice 000000000004 Project 304.RA24020.001.pdf",
        "letterDate": "2026-08-14",
        "letterFrom": "Ron Whitmore, Mitali Ganguly, Raimi + Associates, an Alta Company",
        "firmsOnInvoice": [
            "HHF Planners",
            "Keith Mattson",
            "Raimi + Associates, an Alta Company",
        ],
        "packetNotes": [
            "Pages 1–2: Project Status Report dated August 14, 2026 (May 23–June 30 work).",
            "Pages 3–8: Attachment 1, Scope Tasks + Deliverables status table.",
            "Page 9: professional-services billing table.",
            "Printed prior-billed amounts on some lines do not match Invoice 9 ending totals.",
        ],
    },
    INV10_LINES,
    INV10_NOTES,
    INV10_PAGES,
)

out = Path(__file__).resolve().parent
(out / "invoice9.json").write_text(json.dumps(inv9, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(out / "invoice10.json").write_text(json.dumps(inv10, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", out / "invoice9.json")
print("wrote", out / "invoice10.json")
