const BASE_PATH = "/agent-harness";   // <- slug (1 of 3)
// Old slug kept alive: a resume went out with wxl3.com/harness. Temporary (302) on
// purpose so it never caches stale in a browser if the live slug is renamed again.
const LEGACY_PATH = "/harness";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === LEGACY_PATH || url.pathname.startsWith(`${LEGACY_PATH}/`)) {
      const rest = url.pathname.slice(LEGACY_PATH.length);
      const dest = new URL(request.url);
      dest.pathname = `${BASE_PATH}${rest || "/"}`;
      return Response.redirect(dest.toString(), 302);
    }
    if (url.pathname === BASE_PATH) {
      url.pathname = `${BASE_PATH}/`;
      url.search = "";
      return Response.redirect(url.toString(), 308);
    }
    if (!url.pathname.startsWith(`${BASE_PATH}/`)) {
      return new Response("Not found", { status: 404 });
    }
    const assetUrl = new URL(request.url);
    assetUrl.pathname = url.pathname.slice(BASE_PATH.length) || "/";
    return env.ASSETS.fetch(new Request(assetUrl, request));
  },
};
