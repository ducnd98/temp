# Forms & Inputs

The `nextjs` skill's `data-fetching.md` covers the wiring (react-hook-form
+ zod + mapping the backend's 422 into field errors). This file covers
the markup: which shadcn components a form is built from.

## Contents

- Forms use FieldGroup + Field
- Choosing a form control
- InputGroup requires InputGroupInput/InputGroupTextarea
- Buttons inside inputs use InputGroup + InputGroupAddon
- Option sets (2-7 choices) use ToggleGroup
- FieldSet + FieldLegend for grouping related fields
- Field validation and disabled states

---

## Forms use FieldGroup + Field

Never raw `div` with `space-y-*` for form layout:

```tsx
<FieldGroup>
  <Field>
    <FieldLabel htmlFor="name">Name</FieldLabel>
    <Input id="name" {...form.register("name")} />
  </Field>
  <Field>
    <FieldLabel htmlFor="type">Type</FieldLabel>
    <Select /* ... */ />
  </Field>
</FieldGroup>
```

`Field orientation="horizontal"` for settings-page-style rows (label
left, control right). `FieldLabel className="sr-only"` for visually
hidden labels (e.g. a search box with a placeholder that already states
its purpose).

## Choosing a form control

| Need | Component |
|---|---|
| Simple text input | `Input` |
| Dropdown, predefined options | `Select` |
| Searchable dropdown | `Combobox` |
| Boolean toggle (settings page) | `Switch` |
| Boolean toggle (form, submitted with the rest) | `Checkbox` |
| Single choice from few options | `RadioGroup` |
| Toggle between 2-5 options | `ToggleGroup` + `ToggleGroupItem` |
| OTP/verification code | `InputOTP` |
| Multi-line text | `Textarea` |
| Numeric range | `Slider` |

A widget's `type` field (`kpi`/`chart`/`table`) is exactly a `Select` or,
if there are only 2-3 values and horizontal space allows, a `ToggleGroup`
— either is more correct than a bare `<select>` or radio buttons stacked
vertically.

## InputGroup requires InputGroupInput/InputGroupTextarea

Never a raw `Input`/`Textarea` inside an `InputGroup`.

**Incorrect:**

```tsx
<InputGroup>
  <Input placeholder="Search widgets..." />
</InputGroup>
```

**Correct:**

```tsx
import { InputGroup, InputGroupInput } from "@/components/ui/input-group";

<InputGroup>
  <InputGroupInput placeholder="Search widgets..." />
</InputGroup>
```

## Buttons inside inputs use InputGroup + InputGroupAddon

Never a `Button` positioned with `absolute` next to a raw `Input`:

**Incorrect:**

```tsx
<div className="relative">
  <Input placeholder="Search..." className="pr-10" />
  <Button className="absolute right-0 top-0" size="icon"><SearchIcon /></Button>
</div>
```

**Correct:**

```tsx
<InputGroup>
  <InputGroupInput placeholder="Search..." />
  <InputGroupAddon>
    <Button size="icon"><SearchIcon data-icon="inline-start" /></Button>
  </InputGroupAddon>
</InputGroup>
```

## Option sets (2-7 choices) use ToggleGroup

Don't loop `Button` with manual active-state tracking:

**Incorrect:**

```tsx
const [range, setRange] = useState("7d");
<div className="flex gap-2">
  {["24h", "7d", "30d"].map((r) => (
    <Button key={r} variant={range === r ? "default" : "outline"} onClick={() => setRange(r)}>
      {r}
    </Button>
  ))}
</div>
```

**Correct:**

```tsx
<ToggleGroup spacing={2} value={[range]} onValueChange={(v) => setRange(v[0])}>
  <ToggleGroupItem value="24h">24h</ToggleGroupItem>
  <ToggleGroupItem value="7d">7d</ToggleGroupItem>
  <ToggleGroupItem value="30d">30d</ToggleGroupItem>
</ToggleGroup>
```

`defaultValue`/`value` shape (array vs string) and the single/multiple
prop differ between `base` and Radix — see
[base-vs-radix.md](base-vs-radix.md#togglegroup) (this project uses
Radix).

## FieldSet + FieldLegend for grouping related fields

Not a `div` with a heading, for related checkboxes/switches/radios:

```tsx
<FieldSet>
  <FieldLegend variant="label">Notifications</FieldLegend>
  <FieldDescription>Choose what triggers an alert.</FieldDescription>
  <FieldGroup className="gap-3">
    <Field orientation="horizontal">
      <Checkbox id="threshold-alerts" />
      <FieldLabel htmlFor="threshold-alerts" className="font-normal">Threshold breaches</FieldLabel>
    </Field>
  </FieldGroup>
</FieldSet>
```

## Field validation and disabled states

Both attributes matter — one styles the wrapper, one the control:

```tsx
// Invalid — data-invalid on Field, aria-invalid on the control.
<Field data-invalid={!!form.formState.errors.name}>
  <FieldLabel htmlFor="name">Name</FieldLabel>
  <Input id="name" aria-invalid={!!form.formState.errors.name} {...form.register("name")} />
  {form.formState.errors.name ? (
    <FieldDescription>{form.formState.errors.name.message}</FieldDescription>
  ) : null}
</Field>

// Disabled — data-disabled on Field, disabled on the control.
<Field data-disabled>
  <FieldLabel htmlFor="name">Name</FieldLabel>
  <Input id="name" disabled />
</Field>
```

This is exactly the shape the `nextjs` skill's react-hook-form + zod
pattern needs — `form.formState.errors.<field>` (whether from zod or
mapped from the backend's 422 response) drives both attributes.
