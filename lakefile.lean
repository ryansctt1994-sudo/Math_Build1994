import Lake
open Lake DSL

package «math-build-v3» where
  -- Minimal Day-1 mathematical operating system package.

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "d568c8c09630de097a046763c17b9ea99f95f950"

@[default_target]
lean_lib MathBuild where
  -- Library root: MathBuild/
