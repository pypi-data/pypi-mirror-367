import { useState } from "react";

const { importWhiteboxComponent } = Whitebox;

const Button = importWhiteboxComponent("ui.button");
const FullscreenExitIcon = importWhiteboxComponent("icons.fullscreen-exit");

const ScrollableOverlay = ({
  openOverlayIcon,
  overlayTitle,
  overlaySubtitle,
  viewExpanded = false,
  children,
}) => {
  const [isExpanded, setIsExpanded] = useState(viewExpanded);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  if (!isExpanded) {
    return (
      <div className="bg-white rounded-2xl h-16 w-16 overflow-hidden flex items-center justify-center">
        <Button leftIcon={openOverlayIcon} onClick={toggleExpand} />
      </div>
    );
  }

  return (
    <div className="c_scrollable_overlay bg-white rounded-3xl w-80 h-full overflow-hidden flex flex-col">
      {/* Header - Fixed */}
      <div className="flex items-center justify-between py-3 px-6 border-b border-gray-5 flex-shrink-0">
        <h2 className="text-xl font-bold">
          {overlayTitle}{" "}
          <span className="text-gray-1 font-thin text-md">
            {overlaySubtitle}
          </span>
        </h2>
        <Button leftIcon={<FullscreenExitIcon />} onClick={toggleExpand} />
      </div>

      {children}
    </div>
  );
};

export default ScrollableOverlay;
export { ScrollableOverlay };
