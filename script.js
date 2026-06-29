function isScrolled(scrollY, threshold = 56) {
  return scrollY > threshold;
}

if (typeof window !== 'undefined') {
  window.isScrolled = isScrolled;
}

function syncNav() {
  const nav = document.querySelector('.site-nav');
  if (!nav) return;
  nav.classList.toggle('is-scrolled', isScrolled(window.scrollY));
}

function setupReveals() {
  const nodes = document.querySelectorAll('[data-reveal]');
  if (!nodes.length) return;
  const cutoff = window.innerHeight * 0.92;

  nodes.forEach((node) => {
    if (node.getBoundingClientRect().top < cutoff) {
      node.classList.add('in-view');
    }
  });

  if (!('IntersectionObserver' in globalThis)) {
    nodes.forEach((node) => node.classList.add('in-view'));
    return;
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
}

if (typeof document !== 'undefined') {
  syncNav();
  setupReveals();
  window.addEventListener('scroll', syncNav, { passive: true });
}
