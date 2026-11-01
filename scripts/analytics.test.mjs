import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

function setup(profile = "", initialUrl = "https://browseawesome.com/repos/?q=private@example.com", comparisonState, readyState = "complete") {
  const events = [];
  const handlers = {};
  let options;
  const ph = {
    init: (_key, opts) => { options = opts; },
    capture: (event, properties) => events.push({ event, properties }),
    identify: (id) => events.push({ event: "identify", id }),
    register: () => {},
    get_property: () => null,
    get_distinct_id: () => "anon-id",
    get_session_id: () => "session-id",
  };
  const location = new URL(initialUrl);
  const document = {
    readyState,
    currentScript: { dataset: { posthogKey: "phc_test", posthogHost: "https://us.i.posthog.com", posthogProfile: profile } },
    addEventListener: (name, callback) => { handlers[name] = callback; },
    querySelector: () => document.readyState === "loading" || comparisonState === undefined ? null : { dataset: { comparisonState } },
  };
  vm.runInNewContext(readFileSync("frontend/src/js/modules/analytics.js", "utf8"), {
    window: { posthog: ph, location }, document, URL, URLSearchParams,
  });
  const client = { ...ph, capture: (event, properties) => events.push({ event, properties }) };
  ph.capture = () => { throw new Error("bootstrap queue used after SDK loaded"); };
  options.loaded(client);
  return { events, handlers, location, options, document };
}

test("one pageview per HTMX URL transition, no raw query", () => {
  const { events, handlers, location } = setup();
  handlers["htmx:pushedIntoHistory"]();
  assert.equal(events.filter((e) => e.event === "$pageview").length, 1);
  location.href = "https://browseawesome.com/repos/?q=other";
  handlers["htmx:pushedIntoHistory"]();
  assert.equal(events.filter((e) => e.event === "$pageview").length, 2);
  assert.ok(!JSON.stringify(events).includes("private@example.com"));
});

test("profile identification and private URL redaction", () => {
  const { events, options } = setup("123");
  assert.equal(events[0].id, "123");
  const event = options.before_send({ properties: { $current_url: "https://browseawesome.com/accounts/confirm/secret?token=secret" } });
  assert.equal(event.properties.$current_url, "https://browseawesome.com/[private]");
});

test("SDK nullable properties survive scrubbing and preserve only the public routing token", () => {
  const { options } = setup();
  const event = options.before_send({ properties: {
    token: "phc_test", $set: null, nested: { value: null, token: "secret" },
    values: [null, { password: "secret" }], authorization: "secret",
  } });
  assert.equal(event.properties.token, "phc_test");
  assert.equal(event.properties.$set, null);
  assert.equal(event.properties.nested.value, null);
  assert.equal(event.properties.nested.token, undefined);
  assert.ok(!JSON.stringify(event).includes("secret"));
  assert.equal(options.before_send({ properties: { token: "private-token" } }).properties.token, undefined);
});

test("task shortcuts emit fixed labels without link text, URLs or query input", () => {
  const { events, handlers } = setup();
  const actions = {
    "awesome-selfhosted/awesome-selfhosted": "directory_self_hosted",
    "vinta/awesome-python": "directory_python",
    "agarrharr/awesome-cli-apps": "directory_cli",
    "bradAGI/awesome-cli-coding-agents": "directory_coding_agents",
    "public-apis/public-apis": "directory_apis",
    directory_checklist: "directory_checklist",
    selfhosted_bookmarks: "selfhosted_bookmarks",
    selfhosted_checklist: "selfhosted_checklist",
    selfhosted_offline_test: "selfhosted_offline_test",
    chatgpt_browser: "chatgpt_browser",
    python_cli_click: "python_cli_click",
    python_cli_typer: "python_cli_typer",
    python_cli_compare: "python_cli_compare",
    chatgpt_telegram: "chatgpt_telegram",
    chatgpt_ollama: "chatgpt_ollama",
    chatgpt_checklist: "chatgpt_checklist",
    coding_agents: "coding_agents",
    coding_multiplexers: "coding_multiplexers",
    coding_harnesses: "coding_harnesses",
    coding_checklist: "coding_checklist",
    coding_mcp_guide: "coding_mcp_guide",
    repository_file_discovery: "repository_file_discovery",
    stack_search_django: "stack_search_django",
    stack_search_fastapi: "stack_search_fastapi",
    stack_search_nextjs: "stack_search_nextjs",
    repository_growth_guide: "repository_growth_guide",
    filter_growth_guide: "filter_growth_guide",
    empty_keep_search: "empty_keep_search",
    empty_reset_filters: "empty_reset_filters",
    empty_browse_lists: "empty_browse_lists",
    empty_remove_license: "empty_remove_license",
    empty_license_guide: "empty_license_guide",
    filter_license_guide: "filter_license_guide",
    repository_compare: "repository_compare",
  };
  for (const [input, output] of Object.entries(actions)) {
    const link = {
      href: "https://browseawesome.com/lists/renamed-list/?q=secret@example.com#private",
      textContent: "private link label",
      dataset: { discoveryAction: input },
    };
    handlers.click({ target: { closest: () => link } });
    const captured = events.at(-1);
    assert.equal(captured.event, "discovery_action_clicked");
    assert.deepEqual(JSON.parse(JSON.stringify(captured.properties)), { action: output });
  }
  assert.equal(events.filter((e) => e.event === "discovery_action_clicked").length, Object.keys(actions).length);
  assert.ok(!JSON.stringify(events).includes("secret@example.com"));
  assert.ok(!JSON.stringify(events).includes("private link label"));
});

test("comparison events describe rendered states, not submitted or matched identities", () => {
  const url = "https://browseawesome.com/tools/compare-github-repositories/?first=secret@example.com&second=private/repo";
  for (const state of ["empty", "example", "prepared", "compared", "unobserved", "invalid"]) {
    const { events, handlers } = setup("", url, state);
    handlers["htmx:pushedIntoHistory"]();
    const views = events.filter((e) => e.event === "repository_comparison_viewed");
    assert.equal(views.length, 1);
    assert.deepEqual(JSON.parse(JSON.stringify(views[0].properties)), { state });
    assert.ok(!JSON.stringify(events).includes("secret@example.com"));
    assert.ok(!JSON.stringify(events).includes("private/repo"));
  }
  for (const state of [undefined, "private/repo", "__proto__"]) {
    const { events } = setup("", url, state);
    assert.equal(events.filter((e) => e.event === "repository_comparison_viewed").length, 0);
  }
  const other = setup("", "https://browseawesome.com/tools/", "compared");
  assert.equal(other.events.filter((e) => e.event === "repository_comparison_viewed").length, 0);
  // A cached SDK may be ready while the body marker has not been parsed yet.
  const early = setup("", url, "compared", "loading");
  assert.equal(early.events.length, 0);
  early.document.readyState = "complete";
  early.handlers.DOMContentLoaded();
  early.handlers["htmx:pushedIntoHistory"]();
  assert.equal(early.events.filter((e) => e.event === "repository_comparison_viewed").length, 1);
  assert.equal(early.events.filter((e) => e.event === "$pageview").length, 1);
});

test("unknown, inherited, unmarked and external actions are not task events", () => {
  const { events, handlers } = setup();
  for (const action of [undefined, "secret@example.com", "__proto__", "toString"]) {
    handlers.click({ target: { closest: () => ({ href: "https://browseawesome.com/lists/", dataset: { discoveryAction: action } }) } });
  }
  handlers.click({ target: { closest: () => null } });
  handlers.click({ target: { closest: () => ({ href: "https://github.com/example/repo?token=secret", dataset: { discoveryAction: "selfhosted_bookmarks" } }) } });
  assert.equal(events.filter((e) => e.event === "discovery_action_clicked").length, 0);
  assert.equal(events.at(-1).event, "github_link_clicked");
  assert.equal(events.at(-1).properties.destination, "https://github.com/example/repo");
});

test("catalog parameter names and sort values are allowlisted on load and HTMX navigation", () => {
  const { events, handlers, location } = setup("", "https://browseawesome.com/lists/?q=private@example.com&private@example.com=x&sort=secret@example.com&language=Python&language=Go&page=-1");
  const first = events.find((e) => e.event === "catalog_browsed").properties;
  assert.equal(first.has_query, true);
  assert.equal(first.sort, "default");
  assert.equal(first.page, 1);
  assert.deepEqual(Array.from(first.filter_names), ["language", "page", "sort"]);
  for (const page of ["Infinity", "NaN", "1.5", "9007199254740992"]) {
    location.href = `https://browseawesome.com/lists/?sort=scanned&page=${page}`;
    handlers["htmx:pushedIntoHistory"]();
    assert.equal(events.at(-1).properties.sort, "scanned");
    assert.equal(events.at(-1).properties.page, 1);
  }
  location.href = "https://browseawesome.com/repos/?sort=stars&page=2&topic=secret@example.com&license=private@example.com";
  handlers["htmx:historyRestore"]();
  assert.equal(events.at(-1).properties.page, 2);
  assert.equal(events.at(-1).properties.sort, "stars");
  assert.deepEqual(Array.from(events.at(-1).properties.filter_names), ["license", "page", "sort", "topic"]);
  assert.ok(!JSON.stringify(events).includes("@example.com"));
});
