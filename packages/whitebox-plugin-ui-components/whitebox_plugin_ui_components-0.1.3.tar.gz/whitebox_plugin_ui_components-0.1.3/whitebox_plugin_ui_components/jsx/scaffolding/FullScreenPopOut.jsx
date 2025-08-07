const { importWhiteboxComponent } = Whitebox;

const FullScreenPopOut = ({ title, onClose, children }) => {
  const Button = importWhiteboxComponent("ui.button");
  const CloseIcon = importWhiteboxComponent("icons.close");

  return (
    <>
      {/* Dark backdrop */}
      <div
        className="fixed inset-0 bg-gray-2 z-40 h-full w-full"
        style={{ backgroundColor: "rgba(0, 0, 0, 0.7)" }}
        onClick={onClose}
      ></div>

      <div className="fixed inset-8 z-50 bg-white rounded-3xl overflow-hidden flex flex-col">
        {/* Heading - Fixed */}
        <div className="flex items-center justify-between border-b border-gray-5 flex-shrink-0 px-8 py-4">
          <h2 className="text-xl font-bold">{title}</h2>
          <Button
            leftIcon={<CloseIcon className="w-10 h-10" />}
            onClick={onClose}
          />
        </div>

        {children}
      </div>
    </>
  );
};

export default FullScreenPopOut;
export { FullScreenPopOut };
