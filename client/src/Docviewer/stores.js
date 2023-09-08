import { writable } from 'svelte/store';

const createWritableStore = (key, startValue) => {
    const { subscribe, set } = writable(startValue);
    
    return {
      subscribe,
      set,
      reset: () => set([]),
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

export const sampledocs = createWritableStore('sampledocs', []);
export const sampleIndex = createWritableStore('sampleIndex', 0);
export const back = createWritableStore("back", "");