/// <reference lib="webworker" />
declare const self: ServiceWorkerGlobalScope;

interface ResourceInfo {
    name: string;
    type: "file" | "directory" | "other";
    mtime: string;
    size: number;
}

async function putInCache(request: Request, response: Response) {
    const cache = await caches.open("v1");
    await cache.put(request, response);
}

async function cacheFirst(
    request: Request,
    preloadResponsePromise: Promise<Response>,
    fallbackUrl: URL,
) {
    // First try to get the resource from the cache
    const responseFromCache = await caches.match(request);
    if (responseFromCache) {
        return responseFromCache;
    }

    // Next try to use the preloaded response, if it's there
    // NOTE: Chrome throws errors regarding preloadResponse, see:
    // https://bugs.chromium.org/p/chromium/issues/detail?id=1420515
    // https://github.com/mdn/dom-examples/issues/145
    // To avoid those errors, remove or comment out this block of preloadResponse
    // code along with enableNavigationPreload() and the "activate" listener.
    const preloadResponse = await preloadResponsePromise;
    if (preloadResponse) {
        console.info("using preload response", preloadResponse);
        putInCache(request, preloadResponse.clone());
        return preloadResponse;
    }

    // Next try to get the resource from the network
    try {
        const responseFromNetwork = await fetch(request.clone());
        // response may be used only once
        // we need to save clone to put one copy in cache
        // and serve second one
        putInCache(request, responseFromNetwork.clone());
        return responseFromNetwork;
    } catch (_error) {
        const fallbackResponse = await caches.match(fallbackUrl);
        if (fallbackResponse) {
            return fallbackResponse;
        }
        // when even the fallback response is not available,
        // there is nothing we can do, but we must always
        // return a Response object
        return new Response("Network error happened", {
            status: 408,
            headers: { "Content-Type": "text/plain" },
        });
    }
}

async function addResourcesToCache(resources: string[]) {
    const todo = resources.concat(); // clone resources (concat with nothing just clones)
    const resourceFiles: string[] = [];
    while (todo.length !== 0) {
        const resource = todo.pop();
        if (resource === undefined) {
            break;
        }
        if (resource.endsWith("/")) {
            const request: ResourceInfo[] = await (
                await fetch(resource)
            ).json();
            for (const resourceInfo of request) {
                switch (resourceInfo.type) {
                    case "file":
                        resourceFiles.push(resource + resourceInfo.name);
                        break;
                    case "directory":
                        todo.push(`${resource}${resourceInfo.name}/`);
                        break;
                    case "other":
                }
            }
        } else {
            resourceFiles.push(resource);
        }
    }
    const cache = await caches.open("v1");
    await cache.addAll(resourceFiles);
}

const PREFETCHED_RESOURCES = ["/templates/", "/static/", "/index.html"];

self.addEventListener("install", (event) => {
    event.waitUntil(addResourcesToCache(PREFETCHED_RESOURCES));
});

self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET") {
        return;
    }

    if (new URL(event.request.url).pathname.startsWith("/api/")) {
        event.respondWith(fetch(event.request));
        return;
    }

    event.respondWith(
        cacheFirst(
            event.request,
            event.preloadResponse,
            new URL("/static/404.html"),
        ),
    );
});
