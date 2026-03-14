const elementTimers = new Map;

function addTimer(element, timerId) {
  const timers = elementTimers.get(element) || [];
  timers.push(timerId)
  elementTimers.set(element, timers);
}
function removeTimerElement(element) {
  const timers = elementTimers.get(element) || [];
  for (const timer of timers) {
    clearInterval(timer);
  }
  elementTimers.delete(element);
}

/**
 *
 * @param {Event} event
 */
function handleEvent(e) {
  e.preventDefault();
  handleTrigger(e.target);
}

/**
 * @param {String} duration
 */
function parseDuration(duration) {
  const parsed = duration.match(/(\d+(?:\.\d+)?(s|ms))/);
  if (!parsed) throw new Error("Unknown duration");
  const num = parseFloat(parsed[1]);
  const type = parsed[2];
  const length = { "s": 1000, "ms": 1 };
  return num * length[type];
}

/**
 * @param {Element|Document} element
 */
function registerHandlers(element) {
  const elements = element.querySelectorAll("[hx-get],[hx-trigger],[hx-target]");

  for (const element of elements) {
    const trigger = element.getAttribute("hx-trigger");
    if (trigger) {
      const [key, duration, ...rest] = trigger.split(" ");
      if (rest.length) throw new Error("Unknown trigger: " + rest);
      const parsedDuration = parseDuration(duration);
      if (key !== "every") throw new Error("Unknown trigger: " + key);
      addTimer(element, setInterval(handleTrigger.bind(null, element), parsedDuration));
    } else {
      if ("onclick" in element) {
        element.onclick = handleEvent;
      }
    }
  }
}

/**
 * @param {Element} element
 */
async function handleTrigger(element) {
  const replaceUrl = element.getAttribute("hx-replace-url");
  const get = element.getAttribute("hx-get");
  const targetSelector = element.getAttribute("hx-target");
  const targetElement = document.querySelector(targetSelector) || element;

  if (replaceUrl && replaceUrl !== "false") {
    const targetUrl = replaceUrl == "true" ? get : replaceUrl;
    if (targetUrl) {
      window.history.replaceState({}, "", targetUrl);
    }
  }

  if (get) {
    const res = await fetch(get, {
      headers: {
        "HX-Request": "true",
        "HX-Trigger": element.id,
        "HX-Target": targetSelector,
        "HX-Current-URL": document.location.href
      }
    });
    const data = await res.text();

    if (!targetElement) {
      console.error("Target element not found! Attempted:", targetSelector);
      return;
    }

    const elements = [targetElement, ...targetElement.querySelectorAll("*")];
    for (const element of elements) {
      removeTimerElement(element);
    }

    targetElement.innerHTML = data;

    registerHandlers(targetElement);
  }
}

window.onload = () => registerHandlers(document);
