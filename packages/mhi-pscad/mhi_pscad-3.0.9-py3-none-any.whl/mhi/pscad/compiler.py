"""
External Compiler Codecs
"""

# ==============================================================================
# Imports
# ==============================================================================

from __future__ import annotations

from pathlib import Path
from typing import (ClassVar, Any, Dict, List, NamedTuple, Optional, Set, Tuple,
                    TYPE_CHECKING)
from xml.etree import ElementTree as ET

from mhi.common.codec import FuzzyCodec
from mhi.common.path import expand_path, shell_folder
from mhi.common.warnings import warn

if TYPE_CHECKING:
    from mhi.pscad import PSCAD

# ==============================================================================
# Exports
# ==============================================================================

__all__ = ('CompilerConfiguration', 'CompilerCodecs')

# ==============================================================================
# Version numbering
# ==============================================================================

VerNum = Tuple[int, ...]
Parameters = Dict[str, Any]

# ==============================================================================
# Compiler Configuration
# ==============================================================================

class CompilerConfiguration(NamedTuple):
    """
    A PSCAD Compiler Configuration
    """

    fortran_version: str
    c_version: str
    matlab_version: str

    def __repr__(self):
        return f"CompilerConfiguration({', '.join(map(repr, self))})"


# ==============================================================================
# ExternalCompilers
# ==============================================================================

class CompilerCodecs:
    """
    Compiler Configuration Coder/Decoder
    """

    def __new__(cls, pscad: Optional[PSCAD]):

        if cls is not CompilerCodecs:
            return object.__new__(cls)

        if not pscad or pscad.version_number < (5, 1):
            return object.__new__(Compilers50)
        return object.__new__(Compilers51)

    _codec: Dict[str, FuzzyCodec]

    @staticmethod
    def _product_list_xml():

        folder = Path(expand_path(r"%PUBLIC%\Documents"))
        if not folder.is_dir():
            folder = shell_folder("Common Documents")
        file = folder / r"Manitoba HVDC Research Centre\ATS\ProductList.xml"
        if not file.is_file():
            raise ValueError("Unable to locate ProductList.xml file")

        doc = ET.parse(file)
        return doc.getroot()


    @classmethod
    def _product_list_maps(cls, key: str, value: str):

        root = cls._product_list_xml()

        return {
            paramlist.get('name', ''): {param.get(key): param.get(value)
                                        for param in paramlist}
            for paramlist in root.findall('paramlist')}


    @staticmethod
    def _make_codecs(mappings: Dict[str, Dict[str, str]]) -> Dict[str, FuzzyCodec]:

        # Matlab is always optional
        mappings['matlab_version'][''] = ''

        return {name: FuzzyCodec(mapping)
                for name, mapping in mappings.items()}

    @property
    def fortran_codec(self) -> FuzzyCodec:
        """
        The Fortran Codec
        """

        return self._codec['fortran_version']

    @property
    def matlab_codec(self) -> FuzzyCodec:
        """
        The Matlab Codec
        """

        return self._codec['matlab_version']

    @property
    def c_codec(self) -> FuzzyCodec:
        """
        The C/Linker/VisualStudios Codec
        """

        return self._codec['c_version']

    def encodes(self, params: Parameters) -> bool:
        """
        Determine if any compiler parameters are present

        This may be used to determine if compiler configuration encoding
        is necessary.
        """

        return any(field in params for field in self._codec)

    def missing_params(self, _params: Parameters) -> bool:
        """
        Determine if a complete set of compiler parameters is present.

        This should be used to determine if the current settings need to
        be retrieved before encoding, or if that step may be skipped.
        """

        return False

    def encode_all(self,
                   params: Parameters, *,
                   current: Optional[Parameters] = None
                   ) -> Parameters:
        """
        Encode compiler parameters from human-readable strings to
        the internal codes used by PSCAD.

        If not all compiler parameters are given, the current parameters
        may be used to ensure a proper configuration is used.
        """

        return self._encode_all(params, current)

    def _encode_all(self,
                    params: Parameters,
                    _current: Optional[Parameters]
                    ) -> Parameters:

        codec = self._codec
        return {key: self._encode(key, val)
                for key, val in params.items()
                if key in codec}

    def _encode(self, field: str, value: str) -> str:
        try:
            return self._codec[field].encode(value)
        except ValueError:
            error_msg = f"{field} cannot be assigned {value!r}"
            raise ValueError(error_msg) from None

    def _encode_to(self, field: str, value: str, active_keys: Set[str]) -> str:
        try:
            return self._codec[field].encode_to(value, active_keys)
        except ValueError:
            error_msg = f"{field} cannot be assigned {value!r}"
            try:
                self._encode(field, value)
                error_msg += ", due to other selected options"
            except ValueError:
                pass
            raise ValueError(error_msg) from None

    def decode_all(self, params: Parameters) -> Parameters:
        """
        Decode known external compiler parameters to human-readable string
        """

        return self._decode_all(params)

    def _decode_all(self, params: Parameters) -> Parameters:

        codec = self._codec
        return {key: codec[key].decode(val) if key in codec else val
                for key, val in params.items()}


class Compilers50(CompilerCodecs):
    """
    External Compilers for PSCAD 5.1+
    """


    _codec50: ClassVar[Dict[str, FuzzyCodec]] = {}

    def __init__(self, _pscad: Optional[PSCAD]):

        if not Compilers50._codec50:
            maps = self._product_list_maps('value', 'name')
            mappings = {'fortran_version': maps['fortran'],
                        'matlab_version': maps['matlab']}
            Compilers50._codec50 = self._make_codecs(mappings)

        self._codec = Compilers50._codec50


class Compilers51(CompilerCodecs):
    """
    External Compilers for PSCAD 5.1+
    """

    _FIELDS = ('fortran_version', 'c_version', 'matlab_version')

    _codec51: ClassVar[Dict[str, FuzzyCodec]] = {}
    _configs: List[CompilerConfiguration]

    def __init__(self, pscad: PSCAD):

        maps = pscad._compilers if pscad else {}
        configs = pscad._compiler_configs if pscad else []

        if maps:
            mappings = {f'{name}_version': val
                        for name, val in maps.items()}
            codec = self._make_codecs(mappings)
        else:
            if not Compilers51._codec51:
                maps = self._product_list_maps('OID', 'value')
                mappings = {'fortran_version': maps['fortran'],
                            'matlab_version': maps['matlab'],
                            'c_version': maps['visual_studios']}
                gcc = {key: 'GCC '+val[9:]
                      for key, val in maps['fortran'].items()
                      if val.startswith('GFortran ')}
                mappings['c_version'].update(gcc)

                Compilers51._codec51 = self._make_codecs(mappings)
            codec = Compilers51._codec51

        self._codec = codec
        self._configs = configs

    def missing_params(self, params: Parameters) -> bool:

        return not all(field in params for field in self._FIELDS)

    def _encode_all(self,
                    params: Parameters,
                    current: Optional[Parameters]
                    ) -> Parameters:

        if not self._configs:
            return super()._encode_all(params, current)

        configs = list(self._configs)
        codec = self._codec

        encoded = {}
        decoded = {}

        for field in self._FIELDS:
            active_keys = {getattr(cfg, field) for cfg in configs}
            coder = codec[field]

            if field in params:
                value = params[field]
                code = self._encode_to(field, value, active_keys)
                encoded[field] = code
            elif len(active_keys) == 1:
                code = next(iter(active_keys))
                if current and (field in current):
                    if code != current[field]:
                        warn(f"Setting {field}={coder.decode(code)!r}")
                        encoded[field] = code
            elif current and field in current:
                current_code = current[field]
                new_code = coder.equivalent(current_code, active_keys)
                if new_code is None:
                    raise ValueError(f"Required field missing: {field}")
                code = new_code
                if code != current_code:
                    encoded[field] = code
            else:
                raise ValueError(f"Required field missing: {field}")

            decoded[field] = coder.decode(code)
            configs = [cfg for cfg in configs if getattr(cfg, field) == code]

        return encoded
