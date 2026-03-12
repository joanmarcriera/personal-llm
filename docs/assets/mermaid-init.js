window.addEventListener("load", function () {
  if (!window.mermaid) {
    return;
  }

  window.mermaid.initialize({
    startOnLoad: true,
    theme: "neutral",
    securityLevel: "loose",
  });
});
