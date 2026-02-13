/**
 * Gmail Label Creator — Google Apps Script Backup
 * =================================================
 * A standalone Apps Script that creates all 80+ labels in your Gmail account.
 * Use this as a backup method if the Python application is unavailable.
 *
 * HOW TO USE:
 * 1. Go to https://script.google.com
 * 2. Click "New project"
 * 3. Delete the default code and paste this entire file
 * 4. Click the "Run" button (▶) at the top
 * 5. Authorize the script when prompted
 * 6. Check the Execution log for progress
 *
 * Author : Angel Evans
 * Version: 1.0.0
 */

function createAllLabels() {
  var labels = [
    // TIMELINE-EVIDENCE
    "TIMELINE-EVIDENCE",
    "TIMELINE-EVIDENCE/Location-Activity",
    "TIMELINE-EVIDENCE/Location-Activity/Google-Maps",
    "TIMELINE-EVIDENCE/Location-Activity/Redfin-Property",
    "TIMELINE-EVIDENCE/Location-Activity/Travel-Transport",
    "TIMELINE-EVIDENCE/Location-Activity/Check-Ins",
    "TIMELINE-EVIDENCE/Communications-Sent",
    "TIMELINE-EVIDENCE/Communications-Sent/Self-Emails",
    "TIMELINE-EVIDENCE/Communications-Sent/To-Contacts",
    "TIMELINE-EVIDENCE/Communications-Sent/Replies",
    "TIMELINE-EVIDENCE/Legal-Court",
    "TIMELINE-EVIDENCE/Legal-Court/Case-Files",
    "TIMELINE-EVIDENCE/Legal-Court/Attorney-Correspondence",
    "TIMELINE-EVIDENCE/Legal-Court/Court-Notices",
    "TIMELINE-EVIDENCE/Government",
    "TIMELINE-EVIDENCE/Government/IRS",
    "TIMELINE-EVIDENCE/Government/SSA",
    "TIMELINE-EVIDENCE/Government/Medicaid-Medicare",
    "TIMELINE-EVIDENCE/Government/Other-Gov",
    "TIMELINE-EVIDENCE/Financial-Transactions",
    "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase",
    "TIMELINE-EVIDENCE/Financial-Transactions/Credit-Cards",
    "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments",
    "TIMELINE-EVIDENCE/Financial-Transactions/Payment-Processors",
    "TIMELINE-EVIDENCE/Financial-Transactions/Bills-Utilities",
    "TIMELINE-EVIDENCE/Medical",
    "TIMELINE-EVIDENCE/Medical/UC-Health",
    "TIMELINE-EVIDENCE/Medical/Colorado-In-Motion",
    "TIMELINE-EVIDENCE/Medical/Insurance",
    "TIMELINE-EVIDENCE/Medical/Appointments",
    "TIMELINE-EVIDENCE/Medical/Prescriptions",
    "TIMELINE-EVIDENCE/Housing",
    "TIMELINE-EVIDENCE/Housing/HQS-Inspections",
    "TIMELINE-EVIDENCE/Housing/Vouchers",
    "TIMELINE-EVIDENCE/Housing/Rent-Payments",
    "TIMELINE-EVIDENCE/Housing/Property-Search",
    // MUSIC
    "MUSIC",
    "MUSIC/Collaborations",
    "MUSIC/Collaborations/Caresse-Rae-Edna",
    "MUSIC/Collaborations/Other-Collabs",
    "MUSIC/Platforms",
    "MUSIC/Platforms/SoundCloud",
    "MUSIC/Platforms/Spotify",
    "MUSIC/Platforms/Suno",
    "MUSIC/Platforms/Donna",
    "MUSIC/Lyrics-Drafts",
    "MUSIC/Copyright-Legal",
    "MUSIC/Distribution",
    // PROJECTS
    "PROJECTS",
    "PROJECTS/SSRN-Academic",
    "PROJECTS/SSRN-Academic/Paper-Generation",
    "PROJECTS/SSRN-Academic/Submissions",
    "PROJECTS/SSRN-Academic/eJournals",
    "PROJECTS/YumYumCode",
    "PROJECTS/GitHub-Dev",
    "PROJECTS/Universal-OZ",
    "PROJECTS/MCT-InTheWild",
    "PROJECTS/Meetaudreyevans",
    "PROJECTS/Tiki-Washbot",
    "PROJECTS/Neurooz",
    "PROJECTS/Alt-Text-ADA",
    "PROJECTS/App-Ideas",
    "PROJECTS/Other-Projects",
    // JOB-SEARCH
    "JOB-SEARCH",
    "JOB-SEARCH/Applications",
    "JOB-SEARCH/Alerts",
    "JOB-SEARCH/Alerts/Indeed",
    "JOB-SEARCH/Alerts/LinkedIn",
    "JOB-SEARCH/Alerts/Other",
    "JOB-SEARCH/Responses",
    "JOB-SEARCH/Interviews",
    // API-KEYS-CREDENTIALS
    "API-KEYS-CREDENTIALS",
    "API-KEYS-CREDENTIALS/API-Keys",
    "API-KEYS-CREDENTIALS/Bot-Tokens",
    "API-KEYS-CREDENTIALS/Passwords",
    "API-KEYS-CREDENTIALS/Licenses",
    // CONTACTS
    "CONTACTS",
    "CONTACTS/Caresse-Lopez",
    "CONTACTS/Church-One20",
    "CONTACTS/Medical-Team",
    "CONTACTS/Legal-Team",
    "CONTACTS/Housing-Contacts",
    "CONTACTS/Other-Important",
    // ORDERS-RECEIPTS
    "ORDERS-RECEIPTS",
    "ORDERS-RECEIPTS/Amazon",
    "ORDERS-RECEIPTS/Google-Play",
    "ORDERS-RECEIPTS/eBay",
    "ORDERS-RECEIPTS/Etsy",
    "ORDERS-RECEIPTS/Subscriptions",
    "ORDERS-RECEIPTS/Other-Purchases",
    // NEWSLETTERS
    "NEWSLETTERS",
    "NEWSLETTERS/Tech",
    "NEWSLETTERS/Finance",
    "NEWSLETTERS/Business",
    "NEWSLETTERS/Other",
    // SOFTWARE-TRACKING
    "SOFTWARE-TRACKING",
    "SOFTWARE-TRACKING/Purchases",
    "SOFTWARE-TRACKING/Trials",
    "SOFTWARE-TRACKING/Licenses",
    "SOFTWARE-TRACKING/Cancellations",
    // SOCIAL-MEDIA
    "SOCIAL-MEDIA",
    "SOCIAL-MEDIA/TikTok",
    "SOCIAL-MEDIA/LinkedIn",
    "SOCIAL-MEDIA/Reddit",
    "SOCIAL-MEDIA/Nextdoor",
    "SOCIAL-MEDIA/Other",
    // FLAGGED-REVIEW
    "FLAGGED-REVIEW"
  ];

  // Get existing labels to avoid duplicates
  var existingLabels = {};
  var userLabels = GmailApp.getUserLabels();
  for (var i = 0; i < userLabels.length; i++) {
    existingLabels[userLabels[i].getName()] = true;
  }

  var created = 0;
  var skipped = 0;
  var errors = 0;

  for (var j = 0; j < labels.length; j++) {
    var labelName = labels[j];

    if (existingLabels[labelName]) {
      Logger.log("SKIP (exists): " + labelName);
      skipped++;
      continue;
    }

    try {
      GmailApp.createLabel(labelName);
      Logger.log("CREATED: " + labelName);
      created++;
      existingLabels[labelName] = true;

      // Pause briefly to avoid rate limits
      if (j % 10 === 0 && j > 0) {
        Utilities.sleep(1000);
      }
    } catch (e) {
      Logger.log("ERROR creating '" + labelName + "': " + e.message);
      errors++;
    }
  }

  Logger.log("========================================");
  Logger.log("SUMMARY");
  Logger.log("  Created: " + created);
  Logger.log("  Skipped: " + skipped);
  Logger.log("  Errors:  " + errors);
  Logger.log("  Total:   " + labels.length);
  Logger.log("========================================");

  // Show a dialog with the summary
  var ui = SpreadsheetApp || null;
  try {
    var htmlOutput = HtmlService.createHtmlOutput(
      "<h2>Gmail Label Creator — Complete</h2>" +
      "<p><b>Created:</b> " + created + "</p>" +
      "<p><b>Skipped (already exist):</b> " + skipped + "</p>" +
      "<p><b>Errors:</b> " + errors + "</p>" +
      "<p><b>Total labels in hierarchy:</b> " + labels.length + "</p>"
    ).setWidth(400).setHeight(250);
    // This will only work if run from a Sheets/Docs bound script
    // For standalone scripts, the Logger output is sufficient
  } catch (e) {
    // Standalone script — Logger output is the primary output
  }
}
