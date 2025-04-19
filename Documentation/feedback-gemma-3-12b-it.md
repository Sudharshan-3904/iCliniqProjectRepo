# Feedback Testing - `gemma-3-12b-it`:

### General Feedback

- It should ask for height weight age gender etc. ask about underlying other lifestyle diseases like diabetes, hypertension, etc.
- And it should always be able to differentiate between critical care, emergency and routine questions.
- The headache question falls under critical / emergency as it my be due to cerebral edema which is life threatening. In such cases, it should suggest immediate first aid and immediate medical attention at neurosurgical hospital.

---

## Prompt Style testing

#### Prompt type: Vague

- `prompt`: what are cancer symptoms
- `response feedback`: no symptoms listed. only disclaimer information displayed

#### Prompt type: Non-specific

- `prompt`: root canal procedure
- `response feedback`: instead of root canal procedure, root canal definition and tooth anatomy displayed

#### Prompt type: Structured

- `prompt`: explain about root canal procedure
- `response feedback`: only relevant but only basic info is given

---

## Follow up testing

#### Head prompt

- `prompt`: persistent productive cought with nausea
- `response feedback`: very relevant and apt further questions for correct diagnosis

#### Single symptom follow up

- `follow up prompt`: one week of productive cough
- `follow up feedback`: apt questions for further diagnosis

#### Multiple symptom follow up

- `follow up prompt`: no allergies, yellow sputum, nausea immediately afte cought, fatigue and body ache. no runny nose. no fever or palpitation. no other allergies
- `follow up feedback`: Good but only lead questions are coming up. After lead questions of maximum two times, any medical chatbot should suggest physician consultation

---

## Open symptom testing

#### Head prompt

- `prompt`: Headaches with vomitting and blurring of vision. Sound and light sensitivity
- `reponse feedback`: apt response

#### General non-specific follow up

- `follow up prompt`: What to expect when seeking medical help
- `follow up feedback`: Good. No further information required but one feedback in general - it doesn't ask about age, gender, height weight etc which is crucial information

---

## Open symptom testing

#### Head prompt

- `prompt`: Joint pain with bleeding gums
- `reponse feedback`: Good

#### General non-specific follow up

- `follow up prompt`: Other possibilities
- `follow up feedback`: apt response, suggested to consult a physician


---

## Multiple Cause Testing

#### Head prompt

- `prompt`: Right shoulder pain, breathlessness, weight gain  and exhaustion
- `reponse feedback`: It should indicate that considering the severity of Symptoms especially when all of these are combined together, immediate medical attention is required to rule out heart disease. Also it can ask for underlying other medical conditions, presently under any medication etc.

#### Possible causes and ways

| Age | Gender | Possiblity |
| -- | -- | -- |
| Above 40 | Female | Mild heart attack |
| Above 40 | Female | Imminent heart attack |
| Above 40 | Male | Onset of kidney degenration |

### Next expected question

1. Questions about diet habits, smoking, alcohol intake etc

---

**System Prompt Changed**

---

## Multiple Cause Testing

#### Head prompt

- `prompt`: Right shoulder pain, breathlessness, weight gain  and exhaustion
- `reponse feedback`: Apt response with the proper questions

#### Possible causes and ways

| Age | Gender | Possiblity |
| -- | -- | -- |
| Above 40 | Female | Mild heart attack |
| Above 40 | Female | Imminent heart attack |
| Above 40 | Male | Onset of kidney degenration |

### Next expected question

1. Questions about diet habits, smoking, alcohol intake etc