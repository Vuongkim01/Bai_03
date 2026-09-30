# Kim Duy Vương
# 20237410
"""
Lab 03-04 - Bài 2: NHÓM DỰ ÁN VÀ NHÂN SỰ 

"""
from __future__ import annotations

import math
from typing import Dict, Optional, Tuple, overload

__all__ = ["Employee", "SoftwareEngineer", "ProjectTeam", "set_lifecycle_logging"]

# --------------------------------------------------------------------------- #
#  Tiện ích chung
# --------------------------------------------------------------------------- #
_lifecycle_logging = True


def set_lifecycle_logging(enabled: bool) -> None:
    """Bật/tắt thông báo vòng đời (destructor) - hữu ích khi chạy nhiều test."""
    global _lifecycle_logging
    _lifecycle_logging = bool(enabled)


def _log(message: str) -> None:
    if _lifecycle_logging:
        try:
            print(message)
        except Exception:  # stdout có thể đã đóng khi thoát interpreter
            pass


def _money(value: float) -> str:
    return f"{value:,.2f}"


def _require_text(value: object, field_name: str) -> str:
    """Chuỗi không rỗng (chuỗi toàn khoảng trắng cũng coi là rỗng). Trả về chuỗi đã strip."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} phải là chuỗi (str), nhận được {type(value).__name__}")
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} không được rỗng")
    return text


def _require_number(value: object, field_name: str) -> float:
    """Số thực hữu hạn. Từ chối bool, NaN, +/-inf và kiểu không phải số."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} phải là số, nhận được {type(value).__name__}")
    try:
        number = float(value)
    except OverflowError:
        raise ValueError(f"{field_name} quá lớn") from None
    if not math.isfinite(number):
        raise ValueError(f"{field_name} phải là số hữu hạn (không NaN/vô cùng)")
    return number


# --------------------------------------------------------------------------- #
#  Lớp Employee
# --------------------------------------------------------------------------- #
class Employee:
    """Nhân sự thông thường.

    Bất biến: mã không rỗng; họ tên không rỗng; lương cơ bản >= 0 và hữu hạn.
    """

    DEFAULT_ID = "UNKNOWN"
    DEFAULT_FULL_NAME = "Unnamed employee"
    DEFAULT_BASE_SALARY = 0.0

    # --- Ba constructor nạp chồng ------------------------------------------
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, employee_id: str, full_name: str) -> None: ...
    @overload
    def __init__(self, employee_id: str, full_name: str, base_salary: float) -> None: ...

    def __init__(self, *args) -> None:
        self._employee_ready = False  # chỉ đối tượng dựng xong mới in thông báo hủy

        if len(args) == 0:
            employee_id, full_name = self.DEFAULT_ID, self.DEFAULT_FULL_NAME
            base_salary = self.DEFAULT_BASE_SALARY
        elif len(args) == 2:
            employee_id, full_name = args
            base_salary = self.DEFAULT_BASE_SALARY
        elif len(args) == 3:
            employee_id, full_name, base_salary = args
        else:
            raise TypeError(f"Employee() nhận 0, 2 hoặc 3 tham số, nhận được {len(args)}")

        self._id = _require_text(employee_id, "Mã nhân sự")
        self._full_name = _require_text(full_name, "Họ tên")
        salary = _require_number(base_salary, "Lương cơ bản")
        if salary < 0:
            raise ValueError("Lương cơ bản không được âm")
        self._base_salary = salary + 0.0  # chuẩn hóa -0.0 thành 0.0
        self._employee_ready = True

    # --- Destructor ----------------------------------------------------------
    def __del__(self) -> None:
        if getattr(self, "_employee_ready", False):
            _log(f"[~Employee] Hủy nhân sự {self._id} - {self._full_name}")

    # --- Getter --------------------------------------------------------------
    @property
    def id(self) -> str:
        return self._id

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def base_salary(self) -> float:
        return self._base_salary

    # --- Nạp chồng increase_salary -------------------------------------------
    @overload
    def increase_salary(self, amount: float) -> None: ...
    @overload
    def increase_salary(self, value: float, by_percentage: bool) -> None: ...

    def increase_salary(self, value: float, by_percentage: bool = False) -> None:
        """Tăng lương.

        * increase_salary(amount)              : tăng một số tiền cố định.
        * increase_salary(value, True)         : tăng value % lương cơ bản hiện tại.
        * increase_salary(value, False)        : tăng số tiền cố định.
        Giá trị tăng phải dương. Nếu lỗi thì lương giữ nguyên (thao tác nguyên tử).
        """
        amount = _require_number(value, "Giá trị tăng")
        if not isinstance(by_percentage, bool):
            raise TypeError("by_percentage phải là bool")
        if amount <= 0:
            raise ValueError("Giá trị tăng phải dương")

        if by_percentage:
            new_salary = self._base_salary + self._base_salary * amount / 100.0
        else:
            new_salary = self._base_salary + amount
        if not math.isfinite(new_salary):
            raise ValueError("Lương sau khi tăng vượt quá giới hạn biểu diễn")
        self._base_salary = new_salary

    # --- Phương thức "virtual" (mọi phương thức Python đều có thể bị ghi đè) --
    def calculate_monthly_cost(self) -> float:
        """Chi phí hằng tháng; mặc định bằng lương cơ bản."""
        return self._base_salary

    def display_info(self) -> None:
        print(f"[Employee] {self._id} | {self._full_name} | "
              f"Lương cơ bản: {_money(self._base_salary)} | "
              f"Chi phí/tháng: {_money(self.calculate_monthly_cost())}")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self._id!r}, full_name={self._full_name!r})"


# --------------------------------------------------------------------------- #
#  Lớp SoftwareEngineer
# --------------------------------------------------------------------------- #
class SoftwareEngineer(Employee):
    """Kỹ sư phần mềm: kế thừa Employee, thêm ngôn ngữ chính và phụ cấp kỹ thuật.

    Bất biến bổ sung: ngôn ngữ chính không rỗng; phụ cấp >= 0.
    """

    # --- Hai constructor nạp chồng -------------------------------------------
    @overload
    def __init__(self, employee_id: str, full_name: str, primary_language: str) -> None: ...
    @overload
    def __init__(self, employee_id: str, full_name: str, base_salary: float,
                 primary_language: str, technical_allowance: float) -> None: ...

    def __init__(self, employee_id: str, full_name: str, *args) -> None:
        self._engineer_ready = False

        if len(args) == 1:                       # (id, name, language)
            (primary_language,) = args
            base_salary = Employee.DEFAULT_BASE_SALARY
            technical_allowance = 0.0
        elif len(args) == 3:                     # (id, name, salary, language, allowance)
            base_salary, primary_language, technical_allowance = args
        else:
            raise TypeError("SoftwareEngineer() nhận (id, name, language) hoặc "
                            f"(id, name, salary, language, allowance); nhận được {2 + len(args)} tham số")

        language = _require_text(primary_language, "Ngôn ngữ lập trình chính")
        allowance = _require_number(technical_allowance, "Phụ cấp kỹ thuật")
        if allowance < 0:
            raise ValueError("Phụ cấp kỹ thuật không được âm")

        super().__init__(employee_id, full_name, base_salary)  # kiểm tra id/name/lương
        self._primary_language = language
        self._technical_allowance = allowance + 0.0
        self._engineer_ready = True

    # --- Destructor: lớp con in trước, rồi gọi destructor lớp cha ---------------
    def __del__(self) -> None:
        if getattr(self, "_engineer_ready", False):
            _log(f"[~SoftwareEngineer] Hủy kỹ sư {self._id} - {self._full_name} "
                 f"({self._primary_language})")
        super().__del__()

    @property
    def primary_language(self) -> str:
        return self._primary_language

    @property
    def technical_allowance(self) -> float:
        return self._technical_allowance

    # --- Ghi đè ------------------------------------------------------------------
    def calculate_monthly_cost(self) -> float:
        return self._base_salary + self._technical_allowance

    def display_info(self) -> None:
        print(f"[SoftwareEngineer] {self._id} | {self._full_name} | "
              f"Ngôn ngữ: {self._primary_language} | "
              f"Lương cơ bản: {_money(self._base_salary)} | "
              f"Phụ cấp: {_money(self._technical_allowance)} | "
              f"Chi phí/tháng: {_money(self.calculate_monthly_cost())}")


# --------------------------------------------------------------------------- #
#  Lớp ProjectTeam
# --------------------------------------------------------------------------- #
class ProjectTeam:
    """Nhóm dự án: kết tập (aggregation) Employee, không sở hữu vòng đời của họ.

    Bất biến:
      I1. Mã dự án, tên dự án không rỗng.
      I2. Không có hai thành viên cùng mã trong một nhóm.
      I3. Một đối tượng nhân sự không xuất hiện hai lần trong cùng nhóm.
      I4. Nếu có trưởng nhóm thì trưởng nhóm phải nằm trong danh sách thành viên.
      I5. Hủy nhóm không hủy Employee.

    Thành viên lưu trong dict {mã -> Employee} (giữ thứ tự thêm, tra cứu O(1)).
    """

    # --- Hai constructor nạp chồng -------------------------------------------
    @overload
    def __init__(self, project_code: str, project_name: str) -> None: ...
    @overload
    def __init__(self, project_code: str, project_name: str, leader: Employee) -> None: ...

    def __init__(self, *args) -> None:
        self._team_ready = False
        self._members: Dict[str, Employee] = {}
        self._leader: Optional[Employee] = None

        if len(args) == 2:
            project_code, project_name = args
            leader = None
        elif len(args) == 3:
            project_code, project_name, leader = args
            self._require_employee(leader)
        else:
            raise TypeError(f"ProjectTeam() nhận 2 hoặc 3 tham số, nhận được {len(args)}")

        self._project_code = _require_text(project_code, "Mã dự án")
        self._project_name = _require_text(project_name, "Tên dự án")

        if leader is not None:  # trưởng nhóm tự động được đưa vào danh sách thành viên
            self._members[leader.id] = leader
            self._leader = leader

        self._team_ready = True
        self.check_invariants()

    # --- Destructor: chỉ hủy cấu trúc danh sách nội bộ -------------------------
    def __del__(self) -> None:
        members = getattr(self, "_members", None)
        if getattr(self, "_team_ready", False) and members is not None:
            _log(f"[~ProjectTeam] Hủy nhóm {self._project_code}: chỉ gỡ {len(members)} liên kết, "
                 f"KHÔNG hủy các đối tượng Employee")
        if members is not None:
            members.clear()
        self._leader = None

    # --- Getter -----------------------------------------------------------------
    @property
    def project_code(self) -> str:
        return self._project_code

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def leader(self) -> Optional[Employee]:
        return self._leader

    @property
    def members(self) -> Tuple[Employee, ...]:
        """Bản sao chỉ-đọc của danh sách thành viên."""
        return tuple(self._members.values())

    @property
    def member_count(self) -> int:
        return len(self._members)

    # --- Nạp chồng add_member --------------------------------------------------
    @overload
    def add_member(self, employee: Employee) -> bool: ...
    @overload
    def add_member(self, employee: Employee, make_leader: bool) -> bool: ...

    def add_member(self, employee: Employee, make_leader: bool = False) -> bool:
        """Thêm thành viên. Trả về False (không đổi trạng thái) nếu trùng mã.

        * make_leader=True : nhân sự được thêm và trở thành trưởng nhóm; trưởng nhóm cũ
          vẫn là thành viên.
        * Nếu nhân sự đã có trong nhóm thì bị từ chối kể cả khi make_leader=True
          (muốn thăng chức người đã có mặt, dùng change_leader()).
        """
        self._require_employee(employee)
        if not isinstance(make_leader, bool):
            raise TypeError("make_leader phải là bool")
        if employee.id in self._members:
            return False
        self._members[employee.id] = employee
        if make_leader:
            self._leader = employee
        self.check_invariants()
        return True

    def remove_member(self, employee_id: str) -> bool:
        """Xóa thành viên theo mã. False nếu không tìm thấy hoặc đang là trưởng nhóm."""
        key = self._normalize_id(employee_id)
        member = self._members.get(key)
        if member is None:
            return False
        if member is self._leader:      # phải đổi trưởng nhóm trước khi xóa
            return False
        del self._members[key]
        self.check_invariants()
        return True

    def change_leader(self, employee: Employee) -> bool:
        """Đặt trưởng nhóm mới; tự thêm vào nhóm nếu chưa là thành viên.

        Trả về True nếu sau lời gọi `employee` là trưởng nhóm. Trả về False nếu đã có một
        đối tượng *khác* mang cùng mã trong nhóm (tránh vi phạm tính duy nhất của mã).
        """
        self._require_employee(employee)
        existing = self._members.get(employee.id)
        if existing is not None and existing is not employee:
            return False
        if existing is None:
            self._members[employee.id] = employee
        self._leader = employee
        self.check_invariants()
        return True

    def contains(self, employee_id: str) -> bool:
        return self._normalize_id(employee_id) in self._members

    def calculate_total_monthly_cost(self) -> float:
        """Tổng chi phí hằng tháng - gọi đa hình calculate_monthly_cost() của từng thành viên."""
        return sum((m.calculate_monthly_cost() for m in self._members.values()), 0.0)

    def display_team(self) -> None:
        print(f"=== Nhóm dự án [{self._project_code}] {self._project_name} ===")
        if self._leader is None:
            print("Trưởng nhóm : (chưa có)")
        else:
            print(f"Trưởng nhóm : {self._leader.full_name} ({self._leader.id})")
        print(f"Thành viên  : {len(self._members)} người  (* = trưởng nhóm)")
        if not self._members:
            print("  (danh sách trống)")
        for index, member in enumerate(self._members.values(), start=1):
            tag = "*" if member is self._leader else " "
            print(f"  {index:>2}.{tag}", end=" ")
            member.display_info()       # lời gọi đa hình

    # --- Kiểm tra bất biến -------------------------------------------------------
    def check_invariants(self) -> None:
        """Ném RuntimeError nếu một bất biến bị vi phạm."""
        if not self._project_code or not self._project_name:
            raise RuntimeError("Vi phạm I1: mã/tên dự án rỗng")
        for key, employee in self._members.items():
            if key != employee.id or not key:
                raise RuntimeError("Vi phạm I2: khóa danh sách không khớp mã nhân sự")
        if len({id(e) for e in self._members.values()}) != len(self._members):
            raise RuntimeError("Vi phạm I3: một nhân sự xuất hiện hai lần")
        if self._leader is not None and self._members.get(self._leader.id) is not self._leader:
            raise RuntimeError("Vi phạm I4: trưởng nhóm không thuộc danh sách thành viên")

    # --- Hàm nội bộ ---------------------------------------------------------------
    @staticmethod
    def _require_employee(employee: object) -> None:
        if not isinstance(employee, Employee):
            raise TypeError(f"Cần một đối tượng Employee, nhận được {type(employee).__name__}")

    @staticmethod
    def _normalize_id(employee_id: object) -> str:
        if not isinstance(employee_id, str):
            raise TypeError(f"Mã nhân sự phải là chuỗi, nhận được {type(employee_id).__name__}")
        return employee_id.strip()

    def __repr__(self) -> str:
        return (f"ProjectTeam(code={self._project_code!r}, name={self._project_name!r}, "
                f"members={len(self._members)})")
