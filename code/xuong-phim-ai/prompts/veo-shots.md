# Veo 3.1 — Shot Prompt Format & Examples

Dùng trong Google Flow → Veo 3.1 sau khi có Character Reference Sheet.
Upload 2-3 reference images per shot, paste prompt, chọn duration.

---

## Prompt Format

```
Subject: [stick figure description — specific, not generic]
Action: [precise physical movement — verb + object + direction]
Camera: [shot size, angle, movement]
Lighting: [source + direction + quality]
Constraints: [background, style, palette, what NOT to include]
Duration: [5s | 8s | 15s]
```

---

## Example 1 — Static Demonstration Shot

**Shot description:** "Minh holds flashlight pointing at prism, rainbow appears on wall, medium side shot"

```
Subject: Small stick figure with round glasses outline holding cylindrical flashlight shape at waist height, slight forward lean

Action: Slowly raises flashlight toward triangular prism shape, beam line extends from flashlight tip through prism apex, rainbow band of 6 color stripes fans outward onto white surface beside figure

Camera: Medium shot, side angle, static camera

Lighting: Diffuse overhead light, flat even illumination from directly above, whiteboard studio quality, no cast shadows

Constraints: Pure white background, stick figure animation style consistent with uploaded reference images, blue (#2563EB) and orange (#EA580C) accents for highlights only, rainbow colors allowed for spectrum visualization, no photorealistic rendering, no drop shadows, minimalist whiteboard aesthetic

Duration: 8s
```

---

## Example 2 — Character Movement Shot

**Shot description:** "Minh walks in from left side carrying prism, sets it on invisible table, medium front shot"

```
Subject: Small stick figure without glasses, wearing simple backpack outline shape, carrying triangular prism shape in right hand

Action: Walks in from left edge of frame with natural stride, reaches center, bends arm to place prism shape on invisible surface, straightens up and looks toward camera

Camera: Medium shot, front angle, static camera

Lighting: Diffuse overhead light, flat even illumination, no directional shadows, whiteboard studio lighting

Constraints: Pure white background, stick figure walking animation consistent with reference images, blue and orange accent colors only, no background elements, no photorealistic texture, clean minimalist style

Duration: 8s
```

---

## Example 3 — Camera Movement Shot

**Shot description:** "Close-up of prism with light beam entering and spectrum exiting, camera slowly zooms in"

```
Subject: Triangular prism shape (outline only, blue accent edges), white light beam entering left side, spectrum of 6 color bands exiting right side

Action: Light beam travels through prism from left input face to right output face, spectrum fans outward in arc shape, slight shimmer on prism edges

Camera: Medium close-up starting, slow zoom-in to close-up over 8 seconds, centered on prism

Lighting: Bright flat lighting, light beam itself is brightest element, prism edges have subtle blue highlight, no ambient shadows

Constraints: Pure white background, diagram-style scientific illustration aesthetic, rainbow colors for spectrum only, blue outline for prism shape, no photorealistic glass material rendering, no refraction distortion, clean educational diagram feel

Duration: 8s
```

---

## Duration Guide

| Clip type | Duration |
|---|---|
| Simple pose / reaction | 5s |
| Standard action / dialogue moment | 8s |
| Complex multi-step action | 15s |
| Diagram / concept animation | 8s |

## Approve / Reject Checklist

| Tiêu chí | Approve ✅ | Reject ❌ |
|---|---|---|
| Nhân vật | Giống reference sheet | Style khác, màu lạ |
| Action | Đúng với description | Sai chuyển động |
| Camera | Đúng framing | Sai góc quay |
| Background | Trắng sạch | Có texture, shadow |
| Màu | Chỉ blue + orange (+ rainbow nếu cần) | Màu ngẫu nhiên |
| Chất lượng | Mượt, không glitch | Artifact, deform |

## Nếu Reject

1. Regenerate 2-3 lần trước khi sửa prompt
2. Nếu character drift: thêm "strictly follow uploaded reference images" vào constraints
3. Nếu background không trắng: thêm "IMPORTANT: pure white background, no grey, no gradient"
4. Nếu action sai: đơn giản hóa action thành 1 bước duy nhất
