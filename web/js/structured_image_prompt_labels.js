import { app } from "/scripts/app.js";

const LABELS = {
  "style": "style",
  "camera angle": "camera angle",
  "lighting": "lighting",
  "background": "background",
  "characters": "characters",
  "action": "action",
  "clothing": "clothing",
  "assets": "assets",
  "quality tags": "quality tags",
  "negative prompt": "negative prompt",
};

const LEGACY_LABELS = [
  "BILDSTIL / LOOK",
  "KAMERA / BILDWINKEL",
  "BELEUCHTUNG",
  "HINTERGRUND / SETTING",
  "CHARAKTERE",
  "HANDLUNG / POSE",
  "KLEIDUNG",
  "ASSETS / REQUISITEN",
  "QUALITAET / DETAILS",
  "NEGATIVER PROMPT",
];

function normalizeName(name) {
  const legacyIndex = LEGACY_LABELS.indexOf(name);
  if (legacyIndex >= 0) {
    return Object.keys(LABELS)[legacyIndex];
  }
  return name;
}

function patchWidgetDraw(widget) {
  if (!widget || widget.__icPromptLabelPatched) {
    return;
  }

  const label = LABELS[normalizeName(widget.name)];
  if (!label) {
    return;
  }

  const originalDraw = widget.draw;
  widget.draw = function (ctx, node, widgetWidth, y, height) {
    const labelHeight = 16;
    ctx.save();
    ctx.fillStyle = "rgba(255, 255, 255, 0.72)";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";
    ctx.fillText(label, 8, y + 8);
    ctx.restore();

    if (originalDraw) {
      return originalDraw.call(this, ctx, node, widgetWidth, y + labelHeight, Math.max(10, height - labelHeight));
    }
  };

  const originalComputeSize = widget.computeSize;
  widget.computeSize = function (width) {
    const size = originalComputeSize ? originalComputeSize.call(this, width) : [width, 20];
    return [size[0], size[1] + 16];
  };

  widget.__icPromptLabelPatched = true;
}

function patchNode(node) {
  if (!node || node.comfyClass !== "ICStructuredImagePrompt" || !node.widgets) {
    return;
  }
  for (const widget of node.widgets) {
    patchWidgetDraw(widget);
  }
  node.setDirtyCanvas?.(true, true);
}

app.registerExtension({
  name: "IC.StructuredImagePrompt.Labels",

  nodeCreated(node) {
    patchNode(node);
  },

  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "ICStructuredImagePrompt") {
      return;
    }

    const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = originalOnNodeCreated?.apply(this, arguments);
      patchNode(this);
      return result;
    };
  },
});
