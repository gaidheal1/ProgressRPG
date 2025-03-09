import { checkInternetConnection } from './connectionChecker.js';
import { saveToLocalStorage, getFromLocalStorage } from '../utils/localStorageUtils.js';

export async function submitBugReport(errorDetails) {
  const connectionOk = await checkInternetConnection();
  if (!connectionOk) {
    saveBugReportLocally(errorDetails);
    return;
  }

  try {
    const response = await fetch("/submit-bug-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
        error: errorDetails,
      }),
    });

    if (response.ok) {
      console.log("Bug report submitted successfully.");
      const data = await response.json();
      handleSubmitBugReportResponse(data, errorDetails);
    } else {
      throw new Error("Bug report submission failed.");
    }
  } catch (e) {
    console.error("Error submitting bug report:", e);
    saveBugReportLocally(errorDetails);
  }
}

function saveBugReportLocally(errorDetails) {
  const reports = getFromLocalStorage("bugReports") || [];
  reports.push({ timestamp: new Date().toISOString(), error: errorDetails });
  saveToLocalStorage("bugReports", reports);
}

export async function submitPendingReports() {
  const reports = getFromLocalStorage("bugReports") || [];
  for (const report of reports) {
    await submitBugReport(report);
  }
}

function handleSubmitBugReportResponse(data, report) {
  if (data.success) {
    console.log("Bug report submitted successfully.");
    const remainingReports = getFromLocalStorage("bugReports").filter(
      (r) => r.timestamp !== report.timestamp
    );
    saveToLocalStorage("bugReports", remainingReports);
  } else {
    console.error("Error submitting report:", data.message);
  }
}
