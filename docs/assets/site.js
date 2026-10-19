// Highlights stay inside the block that the reader points at. Nothing else moves on its own.
(function () {
  // A highlight follows the pointer and the focus; a click keeps it until a click elsewhere or Escape.
  let lockedElement = null;
  let turnOffLocked = null;

  function unlock() {
    if (!lockedElement) return;
    const turnOff = turnOffLocked;
    lockedElement.classList.remove("locked");
    lockedElement = null;
    turnOffLocked = null;
    turnOff();
  }

  function highlightable(element, turnOn, turnOff) {
    const unlessLocked = (action) => () => {
      if (!lockedElement) action();
    };
    element.addEventListener("mouseenter", unlessLocked(turnOn));
    element.addEventListener("mouseleave", unlessLocked(turnOff));
    element.addEventListener("focus", unlessLocked(turnOn));
    element.addEventListener("blur", unlessLocked(turnOff));
    element.addEventListener("click", () => {
      if (lockedElement === element) {
        unlock();
        return;
      }
      unlock();
      turnOn();
      lockedElement = element;
      turnOffLocked = turnOff;
      element.classList.add("locked");
    });
  }

  document.addEventListener("click", (event) => {
    if (lockedElement && !lockedElement.contains(event.target)) unlock();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") unlock();
  });

  const highlight = (elements) => elements.forEach((element) => element.classList.add("highlighted"));
  const unhighlight = (elements) => elements.forEach((element) => element.classList.remove("highlighted"));

  // A specification item and its lines point at each other.
  document.querySelectorAll("figure.file-figure").forEach((figure) => {
    const linesOf = (pin) => [...figure.querySelectorAll(`.row[data-pins~="${pin}"]`)];
    const itemOf = (pin) => [...figure.querySelectorAll(`li[data-pin="${pin}"]`)];

    figure.querySelectorAll("li[data-pin]").forEach((item) => {
      const pin = item.dataset.pin;
      const turnOn = () => {
        const lines = linesOf(pin);
        highlight([...lines, item]);
        scrollIntoCode(figure.querySelector("pre"), lines[0]);
      };
      highlightable(item, turnOn, () => unhighlight([...linesOf(pin), item]));
    });

    figure.querySelectorAll(".row[data-pins]").forEach((line) => {
      const pins = line.dataset.pins.split(" ");
      const related = () => [...new Set(pins.flatMap((pin) => [...linesOf(pin), ...itemOf(pin)]))];
      highlightable(line, () => highlight(related()), () => unhighlight(related()));
    });
  });

  // Scrolls a long file so that the line is in view, a third of the way down.
  function scrollIntoCode(code, line) {
    if (!code || !line || code.scrollHeight <= code.clientHeight) return;
    const offset = line.getBoundingClientRect().top - code.getBoundingClientRect().top;
    if (offset < 0 || offset > code.clientHeight - line.offsetHeight) {
      code.scrollTo({ top: code.scrollTop + offset - code.clientHeight / 3, behavior: "smooth" });
    }
  }

  // A command: what each part does and the part point at each other.
  document.querySelectorAll(".command-card").forEach((card) => {
    const both = (pin) => [...card.querySelectorAll(`[data-pin="${pin}"]`)];
    card.querySelectorAll("li[data-pin], .command-part[data-pin]").forEach((element) => {
      const pin = element.dataset.pin;
      highlightable(element, () => highlight(both(pin)), () => unhighlight(both(pin)));
    });
  });

  // File explorers: the tree selects the file that the viewer shows.
  document.querySelectorAll(".explorer").forEach((explorer) => {
    const buttons = explorer.querySelectorAll(".explorer-tree button[data-file]");
    buttons.forEach((button) => button.addEventListener("click", () => {
      buttons.forEach((other) => other.toggleAttribute("aria-current", other === button));
      explorer.querySelectorAll(".explorer-panel").forEach((panel) => {
        panel.hidden = panel.dataset.file !== button.dataset.file;
      });
    }));
  });

  // Account name: what the reader types takes the place of <account-name> on the page, and in what the copy buttons
  // copy. The browser remembers it.
  const ACCOUNT_PLACEHOLDER = "<account-name>";
  const ACCOUNT_STORAGE_KEY = "eks-platform-lab:account-name";
  const accountWalker = document.createTreeWalker(document.querySelector(".page"), NodeFilter.SHOW_TEXT, {
    acceptNode: (text) => text.nodeValue.includes(ACCOUNT_PLACEHOLDER) && text.parentElement.tagName !== "SCRIPT"
      ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP,
  });
  const textsWithPlaceholder = [];
  while (accountWalker.nextNode()) textsWithPlaceholder.push(accountWalker.currentNode);
  const accountSlots = [];
  for (const text of textsWithPlaceholder) {
    const fragment = document.createDocumentFragment();
    text.nodeValue.split(ACCOUNT_PLACEHOLDER).forEach((piece, index) => {
      if (index > 0) {
        const slot = document.createElement("span");
        slot.className = "account-name";
        accountSlots.push(slot);
        fragment.append(slot);
      }
      fragment.append(piece);
    });
    text.replaceWith(fragment);
  }

  const accountInput = document.getElementById("account-name");
  if (accountInput && accountSlots.length) {
    const fill = (value) => accountSlots.forEach((slot) => {
      slot.textContent = value || ACCOUNT_PLACEHOLDER;
      slot.classList.toggle("filled", value !== "");
    });
    accountInput.closest(".account-field").hidden = false;
    try {
      accountInput.value = localStorage.getItem(ACCOUNT_STORAGE_KEY) || "";
    } catch {}
    fill(accountInput.value.trim());
    accountInput.addEventListener("input", () => {
      const value = accountInput.value.trim();
      fill(value);
      try {
        localStorage.setItem(ACCOUNT_STORAGE_KEY, value);
      } catch {}
    });
  }

  // Copy: a command as written, without the numbers of its parts.
  const COPY_ICON = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">'
    + '<rect x="5" y="5" width="9" height="9" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.4"/>'
    + '<path d="M11 5V3.5A1.5 1.5 0 0 0 9.5 2h-6A1.5 1.5 0 0 0 2 3.5v6A1.5 1.5 0 0 0 3.5 11H5" fill="none" '
    + 'stroke="currentColor" stroke-width="1.4"/></svg>';
  const COPIED_ICON = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">'
    + '<path d="M3 8.5l3.2 3L13 4.5" fill="none" stroke="currentColor" stroke-width="1.8" '
    + 'stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const COPY_TITLE = "Copy the command";

  document.querySelectorAll("pre.command").forEach((command) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-button";
    button.innerHTML = COPY_ICON;
    button.title = COPY_TITLE;
    button.setAttribute("aria-label", COPY_TITLE);
    button.addEventListener("click", async () => {
      const copy = command.cloneNode(true);
      copy.querySelectorAll(".pin").forEach((pin) => pin.remove());
      let copied = true;
      try {
        await navigator.clipboard.writeText(copy.textContent.replace(/\n$/, ""));
      } catch {
        copied = false;
      }
      button.innerHTML = copied ? COPIED_ICON : COPY_ICON;
      button.classList.toggle("copied", copied);
      button.title = copied ? "Copied" : "Could not copy. Select the text and copy it.";
      setTimeout(() => {
        button.innerHTML = COPY_ICON;
        button.classList.remove("copied");
        button.title = COPY_TITLE;
      }, 1600);
    });
    command.parentElement.style.position = "relative";
    command.parentElement.appendChild(button);
  });

  // Cost: the total of a day as one bar, and the breakdown as a chart, from the items of the page.
  const costItems = document.getElementById("cost-items");
  if (costItems) drawCost(JSON.parse(costItems.textContent));

  function drawCost(items) {
    const bar = document.getElementById("cost-bar");
    const chart = document.getElementById("cost-chart");
    document.getElementById("cost-sum").textContent = items.reduce((sum, item) => sum + item[1], 0).toFixed(2);
    bar.innerHTML = items.map(([label, amount], index) =>
      `<span data-index="${index}" style="flex-grow:${amount}" aria-label="${label}"></span>`).join("");

    const draw = (tag, attributes, text, parent = chart) => {
      const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
      for (const name in attributes) element.setAttribute(name, attributes[name]);
      if (text != null) element.textContent = text;
      parent.appendChild(element);
      return element;
    };
    const barLeft = 300, barRight = 700, rowHeight = 28, top = 24;
    const maxAmount = Math.ceil(Math.max(...items.map((item) => item[1])) * 2) / 2;
    const height = top + items.length * rowHeight + 6;
    const barWidth = (amount) => (barRight - barLeft) * amount / maxAmount;
    chart.setAttribute("viewBox", `0 0 790 ${height}`);
    for (let amount = 0; amount <= maxAmount + 1e-9; amount += 0.5) {
      const x = barLeft + barWidth(amount);
      draw("line", { x1: x, x2: x, y1: top - 6, y2: height - 4, class: "gridline" });
      draw("text", { x, y: top - 10, "text-anchor": "middle", class: "tick" }, amount.toFixed(1));
    }
    items.forEach(([label, amount, icon], index) => {
      const y = top + index * rowHeight;
      const row = draw("g", { class: "cost-row", "data-index": index });
      draw("rect", { x: 0, y, width: 790, height: rowHeight, class: "hit-area" }, null, row);
      draw("image", { href: icon, x: barLeft - 34, y: y + 2, width: 20, height: 20 }, null, row);
      draw("text", { x: barLeft - 44, y: y + 15, "text-anchor": "end", class: "cost-label" }, label, row);
      draw("rect", { x: barLeft, y: y + 4, width: Math.max(2, barWidth(amount)), height: 15, rx: 3, class: "amount-bar" },
        null, row);
      draw("text", { x: 784, y: y + 16, "text-anchor": "end", class: "cost-value" },
        amount < 0.1 ? amount.toFixed(3) : amount.toFixed(2), row);
    });

    // Pointing at a part of the total, or at a row of the breakdown, lights both and dims the rest.
    const linked = document.querySelectorAll("#cost-bar [data-index], #cost-chart .cost-row");
    const highlightItem = (index) => {
      [bar, chart].forEach((element) => element.classList.toggle("has-highlight", index !== null));
      linked.forEach((element) => element.classList.toggle("highlighted", element.dataset.index === String(index)));
    };
    linked.forEach((element) => {
      element.addEventListener("mouseenter", () => highlightItem(element.dataset.index));
      element.addEventListener("mouseleave", () => highlightItem(null));
    });
  }

  // Jumps inside the page scroll smoothly, and the place where they end glows once.
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    const destination = document.getElementById(decodeURIComponent(link.getAttribute("href").slice(1)));
    if (!destination) return;
    event.preventDefault();
    const step = destination.closest(".step");
    const arrival = step ? step.querySelector(".step-head") : destination;
    arrival.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    history.replaceState(null, "", link.getAttribute("href"));
    arrival.classList.remove("arrived");
    void arrival.offsetWidth; // restarts the glow when the same place is reached again
    arrival.classList.add("arrived");
  });

  // The rail marks the part of the page that is being read.
  const outlineLinks = [...document.querySelectorAll(".outline a[href^='#']")];
  const sections = outlineLinks.map((link) => {
    const target = document.getElementById(link.getAttribute("href").slice(1));
    return (target && target.closest(".step")) || target;
  });

  function markCurrentSection() {
    const readingLine = window.innerHeight * 0.3;
    let current = 0;
    sections.forEach((section, index) => {
      if (section && section.getBoundingClientRect().top <= readingLine) current = index;
    });
    outlineLinks.forEach((link, index) => link.toggleAttribute("aria-current", index === current));
  }

  let frameRequested = false;
  window.addEventListener("scroll", () => {
    if (frameRequested) return;
    frameRequested = true;
    requestAnimationFrame(() => {
      markCurrentSection();
      frameRequested = false;
    });
  }, { passive: true });
  markCurrentSection();
})();
