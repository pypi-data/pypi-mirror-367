import { useEffect } from "react";
import useFlightSessionStore from "./stores/flight_session";
const { importWhiteboxComponent } = Whitebox;

const PrimaryButton = importWhiteboxComponent("ui.button-primary");

const TriggerButton = () => {
  const isFlightSessionLoaded = useFlightSessionStore((state) => state.isLoaded);
  const isFlightSessionActive = (
      useFlightSessionStore((state) => state.isFlightSessionActive())
  );
  const setFlightSession = useFlightSessionStore((state) => state.setFlightSession);
  const toggleFlightSession = (
      useFlightSessionStore((state) => state.toggleFlightSession)
  );

  useEffect(() => {
    return Whitebox.sockets.addEventListener("flight", "message", (event) => {
      const data = JSON.parse(event.data);

      const eligibleTypes = [
        "flight.start",
        "flight.end",
        "on_connect",  // This is used to set the initial state on load
      ];

      if (eligibleTypes.includes(data.type)) {
        const { flight_session } = data;
        setFlightSession(flight_session);
      }
    });
  }, []);

  return (
    <PrimaryButton
      text={isFlightSessionActive ? "End flight" : "Start flight"}
      className="font-semibold"
      // If loading is in progress, disable the button's effect. We are not
      // setting the button to disabled, because it ends up looking like a
      // flicker when the response is super quick.
      onClick={isFlightSessionLoaded ? toggleFlightSession : null}
    />
  );
};

export { TriggerButton };
export default TriggerButton;
