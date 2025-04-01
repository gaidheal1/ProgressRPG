import { JSDOM } from 'jsdom';

const dom = new JSDOM(`
  <!DOCTYPE html>
  <html>
    <body>
      <div id="activity-timer"></div>
      <div id="quest-timer"></div>
      <div id="activity-status-text"></div>
      <div id="quest-status-text"></div>
    </body>
  </html>
`);

global.document = dom.window.document;
global.window = dom.window;

// Example test: DOM manipulation
import { Timer } from './modules/Timer.js';

const timer = new Timer('activity-timer', 'activity', 'empty', 60);
timer.updateDisplay();
console.log('Updated display:', document.getElementById('activity-timer').textContent);