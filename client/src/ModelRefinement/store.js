import { writable } from 'svelte/store';

const createWritableStore = (key, startValue) => {
    const { subscribe, set } = writable(startValue);
    
    return {
      subscribe,
      set,
      useLocalStorage: () => {
        const json = localStorage.getItem(key);
        if (json) {
          set(JSON.parse(json));
        }
        
        subscribe(current => {
          localStorage.setItem(key, JSON.stringify(current));
        });
      }
    };
  }

export const hiddenClusters = createWritableStore('hiddenClusters', []);
export const keywords = createWritableStore('keywords', {})
export const clusters = createWritableStore('clusters', {})
export const highlightedWords = createWritableStore('highlightedWords', [])
export const selectedHighlights = createWritableStore('selectedHighlights', [])
export const selectedWords = createWritableStore('selectedWords', [])