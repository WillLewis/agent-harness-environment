const BASE_PATH = "/harness";   // <- slug (1 of 3)

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
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
