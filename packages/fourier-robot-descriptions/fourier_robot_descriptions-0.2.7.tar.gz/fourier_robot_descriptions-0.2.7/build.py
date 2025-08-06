import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# --- Configuration ---

# The directory where this script is located
CWD = Path(__file__).parent

# Path to the source URDFs
SRC_URDF_DIR = CWD / "src" / "fourier_robot_descriptions" / "assets" / "base_urdf"

# Path to the generated URDFs
GEN_URDF_DIR = CWD / "src" / "fourier_robot_descriptions" / "assets" / "urdf"

# Define the combinations of (base_robot, left_hand, right_hand) to generate.
# Use None if a hand is not to be attached.
COMBINATIONS = [
    ("gr1t1", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
    ("gr1t1", "fourier_left_hand_12dof", "fourier_right_hand_12dof"),
    ("gr1t1", "inspire_left_hand", "inspire_right_hand"),
    ("gr1t2", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
    ("gr1t2", "fourier_left_hand_12dof", "fourier_right_hand_12dof"),
    ("gr1t2", "inspire_left_hand", "inspire_right_hand"),
    ("gr2t2", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
    ("gr2t2", "fourier_left_hand_12dof", "fourier_right_hand_12dof"),
    ("gr2t2", "inspire_left_hand", "inspire_right_hand"),
    ("gr2t2v2", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
    ("gr2t2v2", "fourier_left_hand_12dof", "fourier_right_hand_12dof"),
    ("gr2t2v2", "inspire_left_hand", "inspire_right_hand"),
    ("gr2t2d", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
    ("gr2t2d", "fourier_left_hand_12dof", "fourier_right_hand_12dof"),
    ("gr2t2d", "inspire_left_hand", "inspire_right_hand"),
    ("qinglong", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
    ("gr3", "fourier_left_hand_6dof", "fourier_right_hand_6dof"),
    ("gr3", "fourier_left_hand_12dof", "fourier_right_hand_12dof"),
]

# --- Main Script ---


def attach_hand(base_robot_root, hand_name, effector_link_name, joint_name):
    """
    Attaches a hand URDF to the base robot's XML tree.
    """
    if not hand_name:
        return

    hand_path = SRC_URDF_DIR / f"{hand_name}.urdf"
    if not hand_path.exists():
        print(f"Warning: Hand URDF not found at {hand_path}, skipping.")
        return

    hand_tree = ET.parse(hand_path)
    hand_root = hand_tree.getroot()

    # The first link in the hand's URDF is assumed to be its base link.
    hand_base_link = hand_root.find("link").get("name")

    # Copy all link and joint elements from the hand to the base robot.
    for element in hand_root.findall("link") + hand_root.findall("joint"):
        base_robot_root.append(element)

    # Create the new fixed joint to attach the hand.
    joint = ET.Element("joint", name=joint_name, type="fixed")
    ET.SubElement(joint, "parent", link=effector_link_name)
    ET.SubElement(joint, "child", link=hand_base_link)
    ET.SubElement(joint, "origin", rpy="0 0 0", xyz="0 0 0")
    base_robot_root.append(joint)
    print(f"  Attached {hand_name} to {effector_link_name}")


def generate_urdf(base_robot_name, left_hand_name, right_hand_name):
    """
    Generates a single combined URDF.
    """
    base_robot_path = SRC_URDF_DIR / f"{base_robot_name}.urdf"
    if not base_robot_path.exists():
        print(f"Error: Base robot URDF not found at {base_robot_path}")
        return

    base_tree = ET.parse(base_robot_path)
    base_root = base_tree.getroot()

    # Attach hands
    attach_hand(base_root, left_hand_name, "left_end_effector_link", "L_hand_base_joint")
    attach_hand(base_root, right_hand_name, "right_end_effector_link", "R_hand_base_joint")

    # Write the combined URDF to a new file
    if left_hand_name and right_hand_name and left_hand_name.startswith("fourier"):
        left_suffix = left_hand_name.replace("fourier_left_hand_", "fourier_hand_")
    elif left_hand_name and right_hand_name and left_hand_name.startswith("inspire"):
        left_suffix = left_hand_name.replace("inspire_left_hand", "inspire_hand")
    else:
        raise ValueError(f"left_hand{left_hand_name} and right_hand{right_hand_name} names are not recognized.")
    # right_suffix = right_hand_name.replace("fourier_right_hand_", "") if right_hand_name else "noright"
    output_name = f"{base_robot_name}_{left_suffix}.urdf"
    output_path = GEN_URDF_DIR / output_name

    # Write the file
    base_tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"-> Generated: {output_path.relative_to(CWD)}\n")


def main():
    """
    Main function to run the generation process.
    """
    print("--- Starting URDF Generation ---")

    # Clean and recreate the generated directory
    if GEN_URDF_DIR.exists():
        shutil.rmtree(GEN_URDF_DIR)
    GEN_URDF_DIR.mkdir(parents=True)
    print(f"Cleaned and created directory: {GEN_URDF_DIR}")

    # Generate all combinations
    for base, left, right in COMBINATIONS:
        print(f"Generating combination: {base} + {left} + {right}")
        generate_urdf(base, left, right)

    # copy the base urdf files to the generated directory
    shutil.copytree(SRC_URDF_DIR, GEN_URDF_DIR, dirs_exist_ok=True)

    print("--- URDF Generation Complete ---")


if __name__ == "__main__":
    main()
