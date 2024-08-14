from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QDialog
from pydantic import BaseModel, Field
from composio.tools.local.base import Action
from enum import Enum
import typing as t

class InputType(str, Enum):
    TEXT = "text"
    INTEGER = "integer"
    DOUBLE = "double"
    ITEM = "item"

class InputField(BaseModel):
    name: str
    prompt: str
    input_type: InputType
    default_value: t.Union[str, int, float] = ""
    min_value: t.Optional[t.Union[int, float]] = None
    max_value: t.Optional[t.Union[int, float]] = None
    decimal_places: int = 2
    items: t.Optional[t.List[str]] = None

class UserInputRequest(BaseModel):
    fields: t.List[InputField] = Field(..., description="List of input fields for the form")

class UserInputResponse(BaseModel):
    user_input: dict = Field(..., description="Dictionary of user inputs for each field")

class DynamicForm(QDialog):
    def __init__(self, fields):
        super().__init__()
        self.fields = fields
        self.inputs = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        for field in self.fields:
            layout.addWidget(QLabel(field.prompt))
            
            if field.input_type == InputType.TEXT:
                input_widget = QLineEdit(str(field.default_value))
            elif field.input_type == InputType.INTEGER:
                input_widget = QSpinBox()
                if field.min_value is not None:
                    input_widget.setMinimum(field.min_value)
                if field.max_value is not None:
                    input_widget.setMaximum(field.max_value)
                input_widget.setValue(int(field.default_value) if field.default_value else 0)
            elif field.input_type == InputType.DOUBLE:
                input_widget = QDoubleSpinBox()
                if field.min_value is not None:
                    input_widget.setMinimum(field.min_value)
                if field.max_value is not None:
                    input_widget.setMaximum(field.max_value)
                input_widget.setDecimals(field.decimal_places)
                input_widget.setValue(float(field.default_value) if field.default_value else 0.0)
            elif field.input_type == InputType.ITEM:
                input_widget = QComboBox()
                input_widget.addItems(field.items)
            else:
                raise ValueError(f"Invalid input type: {field.input_type}")
            
            self.inputs[field.name] = input_widget
            layout.addWidget(input_widget)

        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.accept)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def get_inputs(self):
        return {name: self.get_value(widget) for name, widget in self.inputs.items()}

    def get_value(self, widget):
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()

class TakeUserInput(Action[UserInputRequest, UserInputResponse]):
    """
    Useful to get various types of input from the user using a dynamically generated PyQt6 form.
    """

    _display_name = "Take User Input"
    _request_schema = UserInputRequest
    _response_schema = UserInputResponse
    _tags = ["utility", "input"]
    _tool_name = "system"

    def execute(
        self, request_data: UserInputRequest, authorisation_data: dict
    ) -> dict:
        app = QApplication([])
        
        form = DynamicForm(request_data.fields)
        if form.exec():
            user_input = form.get_inputs()
            execution_details = {"executed": True}
            response_data = {"user_input": user_input}
        else:
            execution_details = {"executed": False, "error": "User cancelled input"}
            response_data = {}

        return {"execution_details": execution_details, "response_data": response_data}

if __name__ == "__main__":
    # Example usage
    fields = [
        InputField(name="name", prompt="Enter your name:", input_type=InputType.TEXT, default_value="John Doe"),
        InputField(name="age", prompt="Enter your age:", input_type=InputType.INTEGER, min_value=0, max_value=120),
        InputField(name="height", prompt="Enter your height (m):", input_type=InputType.DOUBLE, min_value=0.0, max_value=3.0, decimal_places=2),
        InputField(name="country", prompt="Select your country:", input_type=InputType.ITEM, items=["USA", "Canada", "UK", "Australia"])
    ]
    print(TakeUserInput().execute(UserInputRequest(fields=fields), {}))