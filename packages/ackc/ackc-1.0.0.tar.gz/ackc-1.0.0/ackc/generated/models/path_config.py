from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.enforcement_mode import EnforcementMode
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.path_config_claim_information_point import PathConfigClaimInformationPoint
  from ..models.method_config import MethodConfig





T = TypeVar("T", bound="PathConfig")



@_attrs_define
class PathConfig:
    """ 
        Attributes:
            name (Union[Unset, str]):
            type_ (Union[Unset, str]):
            path (Union[Unset, str]):
            methods (Union[Unset, list['MethodConfig']]):
            scopes (Union[Unset, list[str]]):
            id (Union[Unset, str]):
            enforcement_mode (Union[Unset, EnforcementMode]):
            claim_information_point (Union[Unset, PathConfigClaimInformationPoint]):
            invalidated (Union[Unset, bool]):
            static_path (Union[Unset, bool]):
            static (Union[Unset, bool]):
     """

    name: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    path: Union[Unset, str] = UNSET
    methods: Union[Unset, list['MethodConfig']] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    id: Union[Unset, str] = UNSET
    enforcement_mode: Union[Unset, EnforcementMode] = UNSET
    claim_information_point: Union[Unset, 'PathConfigClaimInformationPoint'] = UNSET
    invalidated: Union[Unset, bool] = UNSET
    static_path: Union[Unset, bool] = UNSET
    static: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.path_config_claim_information_point import PathConfigClaimInformationPoint
        from ..models.method_config import MethodConfig
        name = self.name

        type_ = self.type_

        path = self.path

        methods: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.methods, Unset):
            methods = []
            for methods_item_data in self.methods:
                methods_item = methods_item_data.to_dict()
                methods.append(methods_item)



        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        id = self.id

        enforcement_mode: Union[Unset, str] = UNSET
        if not isinstance(self.enforcement_mode, Unset):
            enforcement_mode = self.enforcement_mode.value


        claim_information_point: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.claim_information_point, Unset):
            claim_information_point = self.claim_information_point.to_dict()

        invalidated = self.invalidated

        static_path = self.static_path

        static = self.static


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if type_ is not UNSET:
            field_dict["type"] = type_
        if path is not UNSET:
            field_dict["path"] = path
        if methods is not UNSET:
            field_dict["methods"] = methods
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if id is not UNSET:
            field_dict["id"] = id
        if enforcement_mode is not UNSET:
            field_dict["enforcement-mode"] = enforcement_mode
        if claim_information_point is not UNSET:
            field_dict["claim-information-point"] = claim_information_point
        if invalidated is not UNSET:
            field_dict["invalidated"] = invalidated
        if static_path is not UNSET:
            field_dict["staticPath"] = static_path
        if static is not UNSET:
            field_dict["static"] = static

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.path_config_claim_information_point import PathConfigClaimInformationPoint
        from ..models.method_config import MethodConfig
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        type_ = d.pop("type", UNSET)

        path = d.pop("path", UNSET)

        methods = []
        _methods = d.pop("methods", UNSET)
        for methods_item_data in (_methods or []):
            methods_item = MethodConfig.from_dict(methods_item_data)



            methods.append(methods_item)


        scopes = cast(list[str], d.pop("scopes", UNSET))


        id = d.pop("id", UNSET)

        _enforcement_mode = d.pop("enforcement-mode", UNSET)
        enforcement_mode: Union[Unset, EnforcementMode]
        if isinstance(_enforcement_mode,  Unset):
            enforcement_mode = UNSET
        else:
            enforcement_mode = EnforcementMode(_enforcement_mode)




        _claim_information_point = d.pop("claim-information-point", UNSET)
        claim_information_point: Union[Unset, PathConfigClaimInformationPoint]
        if isinstance(_claim_information_point,  Unset):
            claim_information_point = UNSET
        else:
            claim_information_point = PathConfigClaimInformationPoint.from_dict(_claim_information_point)




        invalidated = d.pop("invalidated", UNSET)

        static_path = d.pop("staticPath", UNSET)

        static = d.pop("static", UNSET)

        path_config = cls(
            name=name,
            type_=type_,
            path=path,
            methods=methods,
            scopes=scopes,
            id=id,
            enforcement_mode=enforcement_mode,
            claim_information_point=claim_information_point,
            invalidated=invalidated,
            static_path=static_path,
            static=static,
        )


        path_config.additional_properties = d
        return path_config

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
