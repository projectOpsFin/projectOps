# ProjectOps Documentation

This directory contains the project requirements, planning, architecture, and workflow documentation.

> **Important:** These documents describe the intended system and design baseline. They do not imply that the corresponding features are implemented in the current Odoo add-on.

## Documents

| Document | Contents |
|---|---|
| [Project overview and requirements](project-overview-and-requirements.md) | Project purpose, scope, roles, and functional requirements |
| [Project plan and team governance](project-plan-and-team-governance.md) | Team responsibilities, roadmap, governance, and project risks |
| [System architecture and data design](system-architecture-and-data-design.md) | Target architecture, proposed entities, relationships, and technical design |
| [Workflows and business rules](workflows-and-business-rules.md) | Intended operational workflows, approval rules, calculations, and open decisions |

## Reading order

1. Start with the project overview to understand the goals and scope.
2. Review the workflows and business rules to understand the intended business behavior.
3. Read the architecture and data design to see the proposed technical approach.
4. Use the project plan and governance document for responsibilities and delivery planning.

## Implementation-status note

The current repository contains an Odoo add-on skeleton with module metadata and a single ProjectOps root menu. Custom business models, role-based security, workflows, reports, and automated tests were not present in the repository during the documentation audit. Keep implementation claims in sync with code and tests as development progresses.

[Return to the repository README](../README.md)
