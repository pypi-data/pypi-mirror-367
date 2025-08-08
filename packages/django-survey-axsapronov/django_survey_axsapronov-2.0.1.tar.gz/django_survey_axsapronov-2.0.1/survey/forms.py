import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button
from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from survey.models import Answer
from survey.models import Question

LOGGER = logging.getLogger(__name__)


def mark_option(option, value, correct_answers, user_answers):
    """Помечает опцию CSS классами в зависимости от правильности ответа"""
    if "attrs" not in option:
        option["attrs"] = {}

    if "class" not in option["attrs"]:
        option["attrs"]["class"] = ""

    if value in correct_answers:
        option["attrs"]["answer-valid"] = "true"

    if value in user_answers and value not in correct_answers:
        option["attrs"]["answer-invalid"] = "true"

    return option


class ValidatedRadioSelect(forms.RadioSelect):
    def __init__(self, correct_answers=None, user_answers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_answers = correct_answers or []
        self.user_answers = user_answers or []

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option = mark_option(option, value, self.correct_answers, self.user_answers)
        return option


class ValidatedCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def __init__(self, correct_answers=None, user_answers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_answers = correct_answers or []
        self.user_answers = user_answers or []

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option = mark_option(option, value, self.correct_answers, self.user_answers)
        return option


class ValidatedSelect(forms.Select):
    def __init__(self, correct_answers=None, user_answers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_answers = correct_answers or []
        self.user_answers = user_answers or []

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option = mark_option(option, value, self.correct_answers, self.user_answers)
        return option


# Формы для пошагового прохождения опроса
class SurveyIntroForm(forms.Form):
    """Форма для вводной страницы опроса"""

    start_survey = forms.BooleanField(required=True, widget=forms.HiddenInput, initial=True)


class QuestionAnswerForm(forms.Form):
    """Форма для ответа на вопрос"""

    def __init__(self, question, response=None, survey=None, current_question_index=None, *args, **kwargs):
        self.question = question
        self.response = response
        self.survey = survey
        self.current_question_index = current_question_index
        self.show_correct_answer = kwargs.pop("show_correct_answer", False)
        self.correct_answer = kwargs.pop("correct_answer", None)
        self.read_only = kwargs.pop("read_only", False)

        # Автоматически включаем read-only режим, если передан корректный ответ
        if self.correct_answer and not self.read_only:
            self.read_only = True

        super().__init__(*args, **kwargs)
        self._build_fields()

    def _build_fields(self):
        """Строит поля формы в зависимости от типа вопроса"""
        field_name = f"question_{self.question.id}"

        # Получаем информацию о правильных и пользовательских ответах
        correct_answers = []
        user_answers = []

        if self.response and self.question.correct_answer:
            # Получаем правильные ответы
            correct_answers = [choice.strip() for choice in self.question.get_clean_correct_answer()]

            # Получаем ответы пользователя
            try:
                existing_answer = Answer.objects.get(response=self.response, question=self.question)
                user_answers = existing_answer.values
            except Answer.DoesNotExist:
                pass

        # Создаем виджеты с учетом валидации
        c_payload = {}
        w_payload = {}

        if correct_answers and user_answers:
            c_payload["correct_answers"] = correct_answers
            c_payload["user_answers"] = user_answers

        # if self.read_only:
        #     w_payload["disabled"] = "disabled"
        #     w_payload["readonly"] = "readonly"

        # Создаем виджеты с правильными атрибутами
        widgets = {
            Question.RADIO: ValidatedRadioSelect(attrs={"class": "form-check-input", **w_payload}, **c_payload),
            Question.SELECT: ValidatedSelect(attrs={"class": "form-select", **w_payload}, **c_payload),
            Question.SELECT_MULTIPLE: ValidatedCheckboxSelectMultiple(
                attrs={"class": "form-check-input", **w_payload}, **c_payload
            ),
            Question.TEXT: forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            Question.SHORT_TEXT: forms.TextInput(attrs={"class": "form-control"}),
            Question.INTEGER: forms.NumberInput(attrs={"class": "form-control"}),
            Question.FLOAT: forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            Question.DATE: forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
        widget = widgets.get(self.question.type, forms.TextInput(attrs={"class": "form-control"}))

        fields = {
            Question.TEXT: forms.CharField,
            Question.SHORT_TEXT: forms.CharField,
            Question.RADIO: forms.ChoiceField,
            Question.SELECT: forms.ChoiceField,
            Question.SELECT_MULTIPLE: forms.MultipleChoiceField,
            Question.INTEGER: forms.IntegerField,
            Question.FLOAT: forms.FloatField,
            Question.DATE: forms.DateField,
        }

        field_payload = {}
        if self.question.type in [Question.RADIO, Question.SELECT, Question.SELECT_MULTIPLE]:
            field_payload = {
                "choices": [(choice.strip(), choice.strip()) for choice in self.question.get_clean_choices()],
            }

        self.fields[field_name] = fields[self.question.type](
            label=self.question.text,
            widget=widget,
            required=self.question.required,
            **field_payload,
        )

        # Настраиваем FormHelper для crispy forms
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "space-e"
        self.helper.form_id = "form-question"

        if self.show_correct_answer and self.correct_answer:
            next_url = reverse("survey:question-detail", kwargs={"survey_id": self.survey.id}) + "?next=true"
            submit_button = Button(
                "next_question",
                _("Next question"),
                css_class="btn btn-success",
                onclick=f"window.location.href='{next_url}'",
                css_id="next-question-btn",
            )
        else:
            if self.current_question_index == self.survey.total_questions:
                button_text = _("Finish survey and go to results")
            else:
                button_text = _("Check your answer")
            submit_button = Submit(
                "action_add",
                button_text,
                css_class="btn btn-primary",
                css_id="submit-answer-btn",
            )

        field_css_classes = "form-option-group"

        layout_items = [
            Field(
                field_name,
                css_class=field_css_classes,
                wrapper_class="input-style-1",
            ),
            submit_button,
        ]
        self.helper.layout = Layout(*layout_items)

    def get_answer_value(self):
        """Возвращает значение ответа в правильном формате"""
        field_name = f"question_{self.question.id}"
        if field_name not in self.cleaned_data:
            return None

        value = self.cleaned_data[field_name]

        # Для множественного выбора преобразуем в список
        if self.question.type == Question.SELECT_MULTIPLE:
            if isinstance(value, list):
                return value
            return [value] if value else []

        return value
