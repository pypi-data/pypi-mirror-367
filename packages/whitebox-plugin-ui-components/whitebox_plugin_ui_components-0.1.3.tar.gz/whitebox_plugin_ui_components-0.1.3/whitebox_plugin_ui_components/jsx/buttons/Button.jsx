import Spinner from "../common/Spinner";

const { utils } = Whitebox;

const Button = ({
  typeClass,
  text = null,
  onClick = null,
  leftIcon = null,
  rightIcon = null,
  className = null,
  isLoading = false,
  ...props
}) => {
  let paddingClasses = "px-6 py-3";
  if ((leftIcon || rightIcon) && !text) {
    paddingClasses = "px-3 py-3";
  }

  const computedClassName = utils.getClasses(
    "btn",
    typeClass,
    className,
    paddingClasses,
    "relative"
  );

  return (
    <button className={computedClassName} onClick={onClick} {...props}>
      <Spinner
        className={
          "absolute inset-0 flex items-center justify-center" +
          (isLoading ? " block" : " hidden")
        }
      />

      <div
        className={`flex items-center justify-center gap-2 ${
          isLoading ? "invisible" : ""
        }`}
      >
        {leftIcon && (
          <span className="flex items-center justify-center">{leftIcon}</span>
        )}

        {text && <span className="whitespace-nowrap">{text}</span>}

        {rightIcon && (
          <span className="flex items-center justify-center">{rightIcon}</span>
        )}
      </div>
    </button>
  );
};

export { Button };
export default Button;
