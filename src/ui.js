export function isScrolled(scrollY, threshold = 56) {
  return scrollY > threshold;
}

export function revealVisible(nodes, cutoff) {
  nodes.forEach((node) => {
    if (node.getBoundingClientRect().top < cutoff) {
      node.classList.add('in-view');
    }
  });
}

export function createRevealObserver(nodes) {
  if (!nodes.length) return null;

  if (!('IntersectionObserver' in globalThis)) {
    nodes.forEach((node) => node.classList.add('in-view'));
    return null;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('in-view');
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.18, rootMargin: '0px 0px -40px 0px' }
  );

  nodes.forEach((node) => observer.observe(node));
  return observer;
}
