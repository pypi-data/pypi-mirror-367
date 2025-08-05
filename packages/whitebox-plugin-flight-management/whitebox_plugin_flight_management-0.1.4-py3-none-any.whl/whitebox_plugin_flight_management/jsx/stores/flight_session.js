import { create } from "zustand";

const flightSessionStore = (set, get) => ({
  isLoaded: false,
  flightSession: null,

  // region helpers

  setFlightSession: (session) => {
    set({
      flightSession: session,
      isLoaded: true,
    });
  },

  getFlightSession: () => {
    return get().flightSession;
  },

  isFlightSessionActive: () => {
    const flightSession = get().flightSession;
    return flightSession && flightSession.ended_at === null;
  },

  // endregion helpers

  // region flight session management

  startFlightSession: async () => {
    set({ isLoaded: false });

    const data = {
      type: "flight.start",
    };
    Whitebox.sockets.send("flight", data);
  },

  endFlightSession: async () => {
    set({ isLoaded: false });

    const data = {
      type: "flight.end",
    };
    Whitebox.sockets.send("flight", data);
  },

  toggleFlightSession: async () => {
    const flightSession = get().flightSession;

    if (flightSession && flightSession.ended_at === null) {
      await get().endFlightSession();
    } else {
      await get().startFlightSession();
    }
  },

  // endregion flight session management
});

const useFlightSessionStore = create(flightSessionStore);

export default useFlightSessionStore;
