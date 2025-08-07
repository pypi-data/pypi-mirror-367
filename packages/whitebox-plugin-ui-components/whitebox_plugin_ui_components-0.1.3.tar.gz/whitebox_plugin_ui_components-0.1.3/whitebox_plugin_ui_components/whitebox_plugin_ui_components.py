import whitebox


class WhiteboxPluginUIComponents(whitebox.Plugin):
    name = "UI Components"

    provides_capabilities = ["ui"]
    exposed_component_map = {
        "ui": {
            # Buttons
            "button": "buttons/Button",
            "button-primary": "buttons/PrimaryButton",
            "button-secondary": "buttons/SecondaryButton",
            "button-tertiary": "buttons/TertiaryButton",
            # Other common components
            "spinner": "common/Spinner",
            "input-content-area": "common/InputContentArea",
            "scrollable-overlay": "scaffolding/ScrollableOverlay",
            "full-screen-pop-out": "scaffolding/FullScreenPopOut",
        }
    }


plugin_class = WhiteboxPluginUIComponents
