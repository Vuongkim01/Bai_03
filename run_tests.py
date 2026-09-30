# Kim Duy Vương
# 20237410
"""
run_tests.py - Phần C: chương trình kiểm thử (kịch bản 15 bước + trường hợp biên).

"""
import gc
import math
import sys
import weakref

from hr_models import Employee, ProjectTeam, SoftwareEngineer, set_lifecycle_logging

if hasattr(sys.stdout, "reconfigure"):  # tránh lỗi mã hóa tiếng Việt trên Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

_passed = 0
_failed = 0


# --------------------------------------------------------------------------- #
#  Tiện ích kiểm thử
# --------------------------------------------------------------------------- #
def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def step(number: int, title: str) -> None:
    print(f"\n--- Bước {number}: {title} ---")


def check(label: str, condition: bool) -> None:
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        _failed += 1
        print(f"  [FAIL] {label}")


def expect_raises(label: str, exc_type, func) -> None:
    """Kỳ vọng func() ném exc_type."""
    global _passed, _failed
    try:
        func()
    except exc_type as error:
        _passed += 1
        print(f"  [PASS] {label} -> {exc_type.__name__}: {error}")
    except Exception as error:  # ném sai loại lỗi
        _failed += 1
        print(f"  [FAIL] {label} -> ném {type(error).__name__} thay vì {exc_type.__name__}")
    else:
        _failed += 1
        print(f"  [FAIL] {label} -> không ném lỗi")


# --------------------------------------------------------------------------- #
#  Bước 13-14: khối lệnh cục bộ chứa nhóm thứ hai
# --------------------------------------------------------------------------- #
def demo_second_team(shared: Employee, leader: Employee):
    """Tạo nhóm thứ hai trong phạm vi hàm; nhóm bị hủy khi hàm kết thúc.

    Trả về weakref tới nhóm để bên ngoài chứng minh nhóm đã bị hủy.
    """
    team2 = ProjectTeam("PRJ-002", "Ứng dụng di động", leader)   # constructor có trưởng nhóm
    added = team2.add_member(shared)                             # nhân sự đã có ở nhóm 1
    check(f"Thêm {shared.id} (đã thuộc nhóm 1) vào nhóm 2 thành công", added)
    team2.display_team()
    return weakref.ref(team2)
    # <- ra khỏi hàm: biến cục bộ team2 bị giải phóng => destructor của ProjectTeam chạy


# --------------------------------------------------------------------------- #
#  PHẦN C: kịch bản 15 bước
# --------------------------------------------------------------------------- #
def run_scenario() -> None:
    banner("PHẦN C - KỊCH BẢN KIỂM THỬ (15 bước)")

    step(1, "Tạo hai Employee bằng hai constructor khác nhau")
    e1 = Employee("E01", "Nguyễn Văn An")                    # (id, name)  -> lương = 0
    e2 = Employee("E02", "Trần Thị Bình", 12_000_000)        # (id, name, salary)
    e1.display_info()
    e2.display_info()
    check("e1 (constructor 2 tham số) có lương mặc định 0", e1.base_salary == 0)
    check("e2 (constructor 3 tham số) có lương 12,000,000", e2.base_salary == 12_000_000)

    step(2, "Tạo hai SoftwareEngineer bằng hai constructor khác nhau")
    s1 = SoftwareEngineer("SE01", "Lê Minh Cường", "Python")                      # 3 tham số
    s2 = SoftwareEngineer("SE02", "Phạm Quốc Dũng", 20_000_000, "C++", 3_000_000)  # 5 tham số
    s1.display_info()
    s2.display_info()
    check("s1: lương 0, phụ cấp 0, ngôn ngữ Python",
          (s1.base_salary, s1.technical_allowance, s1.primary_language) == (0, 0, "Python"))
    check("s2: chi phí tháng = 20,000,000 + 3,000,000", s2.calculate_monthly_cost() == 23_000_000)

    step(3, "Tăng lương bằng số tiền cố định (increase_salary(amount))")
    e1.increase_salary(8_000_000)
    check("e1: 0 + 8,000,000 = 8,000,000", e1.base_salary == 8_000_000)

    step(4, "Tăng lương theo phần trăm (increase_salary(value, True))")
    e2.increase_salary(10, True)
    check("e2: 12,000,000 tăng 10% = 13,200,000", math.isclose(e2.base_salary, 13_200_000))

    step(5, "Tạo nhóm dự án không có trưởng nhóm")
    team1 = ProjectTeam("PRJ-001", "Hệ thống quản lý nhân sự")
    team1.display_team()
    check("Nhóm mới chưa có trưởng nhóm và chưa có thành viên",
          team1.leader is None and team1.member_count == 0)

    step(6, "Thêm nhân sự bằng addMember(employee)")
    check("Thêm e1 -> True", team1.add_member(e1) is True)
    check("Thêm e2 -> True", team1.add_member(e2) is True)
    check("Nhóm vẫn chưa có trưởng nhóm", team1.leader is None)

    step(7, "Thêm kỹ sư bằng addMember(employee, True) để làm trưởng nhóm")
    check("Thêm s2 làm trưởng nhóm -> True", team1.add_member(s2, True) is True)
    check("Trưởng nhóm là s2", team1.leader is s2)

    step(8, "Thử thêm lại một thành viên đã tồn tại")
    check("Thêm lại e1 -> False", team1.add_member(e1) is False)
    check("Số thành viên vẫn là 3", team1.member_count == 3)

    step(9, "Hiển thị danh sách bằng lời gọi đa hình")
    team1.display_team()

    step(10, "Tính tổng chi phí nhân sự hằng tháng")
    total = team1.calculate_total_monthly_cost()
    print(f"  Tổng chi phí/tháng = {total:,.2f}")
    check("8,000,000 + 13,200,000 + 23,000,000 = 44,200,000", math.isclose(total, 44_200_000))

    step(11, "Thử xóa trưởng nhóm hiện tại -> phải bị từ chối")
    check("remove_member('SE02') -> False", team1.remove_member("SE02") is False)
    check("s2 vẫn là trưởng nhóm và vẫn thuộc nhóm", team1.leader is s2 and team1.contains("SE02"))

    step(12, "Đổi trưởng nhóm rồi xóa người từng là trưởng nhóm")
    check("change_leader(s1) -> True (s1 chưa là thành viên, được tự thêm)",
          team1.change_leader(s1) is True)
    check("s1 là trưởng nhóm mới và đã thuộc nhóm", team1.leader is s1 and team1.contains("SE01"))
    check("s2 (trưởng nhóm cũ) vẫn là thành viên", team1.contains("SE02"))
    check("remove_member('SE02') -> True", team1.remove_member("SE02") is True)
    check("s2 không còn trong nhóm 1", not team1.contains("SE02"))
    check("s2 vẫn tồn tại như một đối tượng", s2.full_name == "Phạm Quốc Dũng")
    team1.display_team()

    step(13, "Tạo nhóm thứ hai, thêm nhân sự đã có ở nhóm 1 (kết tập nhiều nhóm)")
    step(14, "Hủy nhóm thứ hai bằng cách kết thúc khối lệnh cục bộ (thoát khỏi hàm)")
    e1_ref = weakref.ref(e1)
    s1_ref = weakref.ref(s1)
    team2_ref = demo_second_team(e1, s1)
    gc.collect()  # đảm bảo tương thích cả interpreter không dùng đếm tham chiếu
    print("  (khối lệnh cục bộ đã kết thúc)")

    step(15, "Chứng minh nhân sự của nhóm thứ hai vẫn tồn tại sau khi nhóm bị hủy")
    check("Nhóm 2 đã bị hủy (weakref trả về None)", team2_ref() is None)
    check("e1 vẫn tồn tại", e1_ref() is e1)
    check("s1 (trưởng nhóm cũ của nhóm 2) vẫn tồn tại", s1_ref() is s1)
    e1.display_info()
    s1.display_info()
    check("Nhóm 1 vẫn chứa E01 và SE01", team1.contains("E01") and team1.contains("SE01"))
    check("Nhóm 1 vẫn thỏa mọi bất biến", team1.check_invariants() is None)

    step(16, "(Bổ sung) Hủy luôn nhóm 1 - các nhân sự vẫn còn vì biến cục bộ còn tham chiếu")
    del team1
    gc.collect()
    check("e2 vẫn tồn tại sau khi nhóm 1 bị hủy", e2.full_name == "Trần Thị Bình")
    e2.display_info()

    print("\n>>> Kết thúc kịch bản: các biến cục bộ bị giải phóng, quan sát thông báo destructor "
          "(lớp con in trước, lớp cha in sau):")


# --------------------------------------------------------------------------- #
#  Trường hợp biên
# --------------------------------------------------------------------------- #
def boundary_employee() -> None:
    print("\n--- Biên: Employee ---")
    d = Employee()
    check("Constructor mặc định: UNKNOWN / Unnamed employee / 0",
          (d.id, d.full_name, d.base_salary) == ("UNKNOWN", "Unnamed employee", 0))
    check("Lương = 0 là hợp lệ", Employee("E1", "A", 0).base_salary == 0)
    check("Mã và tên được cắt khoảng trắng hai đầu", Employee("  E1  ", "  An  ").id == "E1")
    expect_raises("Mã rỗng", ValueError, lambda: Employee("", "A"))
    expect_raises("Mã toàn khoảng trắng", ValueError, lambda: Employee("   ", "A"))
    expect_raises("Họ tên rỗng", ValueError, lambda: Employee("E1", ""))
    expect_raises("Lương âm", ValueError, lambda: Employee("E1", "A", -0.01))
    expect_raises("Lương NaN", ValueError, lambda: Employee("E1", "A", float("nan")))
    expect_raises("Lương vô cùng", ValueError, lambda: Employee("E1", "A", float("inf")))
    expect_raises("Lương là chuỗi", TypeError, lambda: Employee("E1", "A", "100"))
    expect_raises("Lương là bool", TypeError, lambda: Employee("E1", "A", True))
    expect_raises("Mã là None", TypeError, lambda: Employee(None, "A"))
    expect_raises("Sai số lượng tham số (1)", TypeError, lambda: Employee("E1"))
    expect_raises("Sai số lượng tham số (4)", TypeError, lambda: Employee("E1", "A", 1, 2))


def boundary_salary() -> None:
    print("\n--- Biên: increase_salary ---")
    emp = Employee("E1", "A", 1000)
    expect_raises("Tăng 0", ValueError, lambda: emp.increase_salary(0))
    expect_raises("Tăng số âm", ValueError, lambda: emp.increase_salary(-5))
    expect_raises("Tăng % âm", ValueError, lambda: emp.increase_salary(-5, True))
    expect_raises("Tăng NaN", ValueError, lambda: emp.increase_salary(float("nan")))
    expect_raises("by_percentage không phải bool", TypeError, lambda: emp.increase_salary(5, "yes"))
    expect_raises("Giá trị tăng là chuỗi", TypeError, lambda: emp.increase_salary("5"))
    check("Sau các lỗi trên lương giữ nguyên 1000", emp.base_salary == 1000)

    emp.increase_salary(100, True)
    check("Tăng 100% : 1000 -> 2000", emp.base_salary == 2000)
    emp.increase_salary(250, True)
    check("Tăng 250% (>100%) vẫn hợp lệ: 2000 -> 7000", emp.base_salary == 7000)
    emp.increase_salary(500, False)
    check("increase_salary(500, False) = tăng cố định: 7000 -> 7500", emp.base_salary == 7500)

    zero = Employee("E2", "B", 0)
    zero.increase_salary(10, True)
    check("Tăng % trên lương 0 hợp lệ và vẫn bằng 0", zero.base_salary == 0)

    huge = Employee("E3", "C", 1e308)
    expect_raises("Tăng gây tràn số", ValueError, lambda: huge.increase_salary(1e308))
    check("Sau khi tràn số, lương giữ nguyên", huge.base_salary == 1e308)


def boundary_engineer() -> None:
    print("\n--- Biên: SoftwareEngineer ---")
    expect_raises("Ngôn ngữ rỗng", ValueError, lambda: SoftwareEngineer("S1", "A", ""))
    expect_raises("Ngôn ngữ toàn khoảng trắng", ValueError, lambda: SoftwareEngineer("S1", "A", "  "))
    expect_raises("Phụ cấp âm", ValueError, lambda: SoftwareEngineer("S1", "A", 100, "Py", -1))
    expect_raises("Lương âm (kiểm tra ở lớp cha)", ValueError,
                  lambda: SoftwareEngineer("S1", "A", -1, "Py", 0))
    expect_raises("Mã rỗng (kiểm tra ở lớp cha)", ValueError, lambda: SoftwareEngineer("", "A", "Py"))
    expect_raises("Thiếu tham số (2)", TypeError, lambda: SoftwareEngineer("S1", "A"))
    expect_raises("Số tham số không khớp constructor nào (4)", TypeError,
                  lambda: SoftwareEngineer("S1", "A", 100, "Py"))

    se = SoftwareEngineer("S1", "A", 1000, "Py", 0)
    check("Phụ cấp = 0 là hợp lệ, chi phí = lương", se.calculate_monthly_cost() == 1000)
    se = SoftwareEngineer("S2", "B", 1000, "Py", 500)
    se.increase_salary(10, True)   # phương thức thừa kế từ Employee
    check("Tăng 10% lương rồi cộng phụ cấp: 1100 + 500 = 1600",
          math.isclose(se.calculate_monthly_cost(), 1600))

    staff = [Employee("E1", "A", 100), SoftwareEngineer("S3", "C", 100, "Go", 50)]
    check("Đa hình qua danh sách Employee: 100 + 150 = 250",
          sum(p.calculate_monthly_cost() for p in staff) == 250)


def boundary_team() -> None:
    print("\n--- Biên: ProjectTeam ---")
    expect_raises("Mã dự án rỗng", ValueError, lambda: ProjectTeam("", "N"))
    expect_raises("Tên dự án rỗng", ValueError, lambda: ProjectTeam("P", ""))
    expect_raises("Trưởng nhóm là None", TypeError, lambda: ProjectTeam("P", "N", None))
    expect_raises("Trưởng nhóm là chuỗi", TypeError, lambda: ProjectTeam("P", "N", "E1"))
    expect_raises("Sai số lượng tham số (1)", TypeError, lambda: ProjectTeam("P"))

    empty = ProjectTeam("P0", "Nhóm rỗng")
    check("Nhóm rỗng: tổng chi phí = 0", empty.calculate_total_monthly_cost() == 0)
    check("Nhóm rỗng: remove_member -> False", empty.remove_member("X") is False)
    check("Nhóm rỗng: contains -> False", empty.contains("X") is False)
    check("contains('') -> False", empty.contains("") is False)
    empty.display_team()

    a, b = Employee(), Employee()  # cùng mã mặc định "UNKNOWN"
    check("Thêm Employee mặc định đầu tiên -> True", empty.add_member(a) is True)
    check("Thêm Employee thứ hai cùng mã UNKNOWN -> False", empty.add_member(b) is False)

    expect_raises("add_member(None)", TypeError, lambda: empty.add_member(None))
    expect_raises("add_member(chuỗi)", TypeError, lambda: empty.add_member("E1"))
    expect_raises("make_leader không phải bool", TypeError,
                  lambda: empty.add_member(Employee("E9", "Z"), "yes"))
    expect_raises("remove_member(mã không phải chuỗi)", TypeError, lambda: empty.remove_member(123))
    check("remove_member('  ') -> False", empty.remove_member("  ") is False)

    lead = Employee("L1", "Trưởng nhóm")
    t = ProjectTeam("P1", "Có trưởng nhóm", lead)
    check("Constructor có trưởng nhóm: leader thuộc danh sách thành viên",
          t.leader is lead and t.member_count == 1 and t.contains("L1"))
    check("Không thể xóa trưởng nhóm dù là thành viên duy nhất", t.remove_member("L1") is False)

    m1 = Employee("M1", "Thành viên 1")
    m2 = Employee("M2", "Thành viên 2")
    t.add_member(m1)
    check("add_member(m1, True) với m1 đã có -> False, trưởng nhóm không đổi",
          t.add_member(m1, True) is False and t.leader is lead)

    clone = Employee("M1", "Trùng mã M1")  # khác đối tượng nhưng cùng mã
    check("Thêm đối tượng khác nhưng trùng mã -> False", t.add_member(clone) is False)
    check("change_leader với đối tượng trùng mã -> False, leader không đổi",
          t.change_leader(clone) is False and t.leader is lead)

    check("change_leader(trưởng nhóm hiện tại) -> True, không đổi số thành viên",
          t.change_leader(lead) is True and t.member_count == 2)
    check("add_member(m2, True): m2 làm trưởng nhóm, trưởng nhóm cũ vẫn là thành viên",
          t.add_member(m2, True) is True and t.leader is m2 and t.contains("L1"))
    check("change_leader sang thành viên có sẵn (m1)", t.change_leader(m1) is True and t.leader is m1)
    check("Xóa trưởng nhóm cũ (m2) sau khi đã đổi -> True", t.remove_member("M2") is True)
    check("Xóa thành viên thường (L1) -> True", t.remove_member("L1") is True)
    check("Xóa lại L1 -> False (không còn)", t.remove_member("L1") is False)
    check("members trả về tuple (không sửa trực tiếp được)", isinstance(t.members, tuple))
    check("Các bất biến vẫn thỏa", t.check_invariants() is None)

    other = ProjectTeam("P2", "Nhóm khác")
    other.add_member(m1)
    t.change_leader(lead)  # lead được thêm lại và làm trưởng nhóm; m1 là thành viên thường
    check("m1 thuộc đồng thời hai nhóm", t.contains("M1") and other.contains("M1"))
    check("Xóa m1 khỏi nhóm 'other' không ảnh hưởng nhóm t",
          other.remove_member("M1") is True and t.contains("M1"))


def run_boundary_tests() -> None:
    banner("KIỂM THỬ CÁC TRƯỜNG HỢP BIÊN")
    set_lifecycle_logging(False)  # tắt thông báo destructor cho gọn
    try:
        boundary_employee()
        boundary_salary()
        boundary_engineer()
        boundary_team()
    finally:
        set_lifecycle_logging(True)


def main() -> int:
    run_scenario()
    run_boundary_tests()
    banner(f"TỔNG KẾT: {_passed} đạt, {_failed} lỗi")
    return 0 if _failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
