// tests/utils/accessibility.js
import { injectAxe, checkA11y } from 'axe-playwright';

export async function testA11y(page, selector = null) {
  await injectAxe(page);
  await checkA11y(page, selector, {
    detailedReport: true,
    detailedReportOptions: { html: true },
  });
}
