import { onBeforeUnmount, onMounted } from 'vue';
import { createRevealObserver, revealVisible } from '../ui.js';

export function useRevealSections() {
  let observer;

  onMounted(() => {
    const nodes = [...document.querySelectorAll('[data-reveal]')];
    revealVisible(nodes, window.innerHeight * 0.92);
    observer = createRevealObserver(nodes);
  });

  onBeforeUnmount(() => {
    observer?.disconnect();
  });
}
