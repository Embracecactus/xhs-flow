// Keep the upstream validator unchanged; adapt only the local browser location.
import {chromium,executablePath} from './browser.mjs';
const launch=chromium.launch.bind(chromium);
chromium.launch=options=>launch({...options,executablePath});
await import('../skills/guizang-social-card-skill/validate-social-deck.mjs');
