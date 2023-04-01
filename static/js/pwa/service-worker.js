const addResourcesToCache = async (resources) => {
    const cache = await caches.open("v1");
    await cache.addAll(resources)
};

const putInCache = async (request, response) => {
    const cache = await caches.open("v1");
    await cache.put(request, response);
};

const cacheFirst = async (request) => {
    const cache = await caches.open("v1");
    const responseFromCache = await cache.match(request);
    const url = request.url
    const responseFromCacheWithOtherSite = await cache.match(url);
    if (url.includes('/watch') || url.includes('/get-new-messages') || request.method === 'POST') {
        return fetch(request)
    }
    if (navigator.onLine) {
        const responseFromNetwork = await fetch(request);
        await putInCache(request, responseFromNetwork.clone());
        return responseFromNetwork;
    }
    else if (responseFromCache) {
        return responseFromCache;
    } else if (responseFromCacheWithOtherSite) {
        return responseFromCacheWithOtherSite;
    } else {
        return "Error no internet";
    }
};

self.addEventListener("install", (event) => {
    event.waitUntil(
        addResourcesToCache([
            "/home",
            "/add",
            "/static/css/base.css",
            "/static/css/form.css",
            "/static/fontawesome/css/all.css",
            "https://cdn.jsdelivr.net/npm/@creativebulma/bulma-tagsinput@1.0.3/dist/css/bulma-tagsinput.min.css",
            "https://cdn.jsdelivr.net/npm/@creativebulma/bulma-tagsinput@1.0.3/dist/js/bulma-tagsinput.min.js",
            "https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css",
            "/static/assets/trickstok_logo_trans.png",
            "",
        ])
    );
});

self.addEventListener("fetch", (event) => {
    event.respondWith(cacheFirst(event.request));
})
