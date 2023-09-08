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

export const selectedCode = createWritableStore('selectedCode', [])
export const highlights = createWritableStore("highlights", [])
export const codes = createWritableStore("codes", [])
export const visitedDocs = createWritableStore("visitedDocs", [])
export const modelHistoryIndex = createWritableStore("modelHistoryIndex", 0)