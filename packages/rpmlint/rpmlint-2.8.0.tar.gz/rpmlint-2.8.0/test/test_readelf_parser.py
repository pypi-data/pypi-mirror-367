from pathlib import Path
import re

import pytest
from rpmlint.checks.BinariesCheck import BinariesCheck
from rpmlint.filter import Filter
from rpmlint.pkg import FakePkg, get_magic
from rpmlint.pkgfile import PkgFile
from rpmlint.readelfparser import ReadelfParser

from Testing import CONFIG, get_tested_path, HAS_32BIT_GLIBC, IS_I686, IS_X86_64


@pytest.fixture(scope='function', autouse=True)
def binariescheck():
    CONFIG.info = True
    output = Filter(CONFIG)
    test = BinariesCheck(CONFIG, output)
    return output, test


def get_full_path(path):
    return str(get_tested_path(Path('readelf', path)))


def readelfparser(path, system_path=None):
    if system_path is None:
        system_path = path
    return ReadelfParser(get_full_path(path), system_path)


def run_elf_checks(test, pkg, pkgfile):
    test._detect_attributes(get_magic(pkgfile.path))
    test.run_elf_checks(pkg, pkgfile)


def test_empty_archive():
    readelf = readelfparser('empty-archive.a')
    assert len(readelf.section_info.elf_files) == 0
    assert len(readelf.symbol_table_info.functions) == 0


def test_simple_archive():
    readelf = readelfparser('main.a')
    assert readelf.is_archive
    assert len(readelf.section_info.elf_files) == 1
    elf_file = readelf.section_info.elf_files[0]
    assert len(elf_file) == 11
    assert elf_file[0].name == '.text'
    assert elf_file[0].size == 21
    assert readelf.symbol_table_info.functions == {'main'}
    assert len(list(readelf.symbol_table_info.get_functions_for_regex(re.compile('mai.')))) == 1


def test_program_header_parsing():
    readelf = readelfparser('nested-function')
    assert len(readelf.program_header_info.headers) == 11
    h0 = readelf.program_header_info.headers[0]
    assert h0.name == 'PHDR'
    assert h0.flags == 'R'
    h9 = readelf.program_header_info.headers[9]
    assert h9.name == 'GNU_STACK'
    assert h9.flags == 'RWE'


def test_dynamic_section_parsing():
    readelf = readelfparser('libutil-2.29.so', '/lib64/libutil-2.29.so')
    assert readelf.is_shlib
    assert not readelf.is_archive
    sections = readelf.dynamic_section_info.sections
    assert len(sections) == 30
    assert sections[0].key == 'NEEDED'
    assert sections[0].value == 'Shared library: [libc.so.6]'
    assert readelf.dynamic_section_info['SYMTAB'] == ['0x4c8']
    assert readelf.dynamic_section_info['NULL'] == ['0x0']
    assert readelf.dynamic_section_info.soname == 'libutil.so.1'
    assert len(readelf.dynamic_section_info.needed) == 1
    assert readelf.dynamic_section_info.needed[0] == 'libc.so.6'


def test_rpath():
    readelf = readelfparser('rpath-lib.so', '/lib64/rpath-lib.so')
    assert readelf.is_shlib
    assert not readelf.is_archive
    assert len(readelf.dynamic_section_info.runpaths) == 1
    assert '/tmp/termcap.so.4' in readelf.dynamic_section_info.runpaths


def test_lto_bytecode(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('lto-object.o'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        assert not test.readelf_parser.parsing_failed_reason()
        out = output.print_results(output.results)
        assert 'lto-bytecode' in out


def test_lto_archive_text(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('stripped-lto.a'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'E: lto-no-text-in-archive' in out
        assert 'E: static-library-without-debuginfo' in out


def test_stripped_archive(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('stripped-archive.a'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'E: static-library-without-symtab' in out


def test_lto_archive_text_function_sections(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('function-sections.a'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        assert 'E: lto-no-text-in-archive' not in output.print_results(output.results)


def test_lto_archive_init_array(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('libbsd-ctor.a'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        assert 'E: lto-no-text-in-archive' not in output.print_results(output.results)


def test_lto_archive_preinit_array(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('libclang_rt.asan-preinit-x86_64.a'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        assert 'E: lto-no-text-in-archive' not in output.print_results(output.results)


def test_lto_archive_with_only_data(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('only-data.a'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        assert 'E: lto-no-text-in-archive' not in output.print_results(output.results)


def test_archive_with_debuginfo(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('archive-with-debuginfo.a'), 'x.a')
        run_elf_checks(test, pkg, pkgfile)
        assert 'E: static-library-without-debuginfo' not in output.print_results(output.results)


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_executable_stack(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('executable-stack'), '/lib64/my/a.out')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)

        if 'ldd-failed' in out:
            pytest.skip("ldd failed, maybe it's a different architecture")

        assert 'E: executable-stack /lib64/my/a.out' in out


def test_readelf_failure():
    readelf = readelfparser('not-existing-file')
    assert 'No such file' in readelf.parsing_failed_reason()


def test_readelf_failure_in_package(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('not-existing.so'), '/lib64/not-existing.so')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'readelf-failed /lib64/not-existing.so' in out


def test_readelf_single_error_message(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('small_archive.a'), '/lib64/small_archive.a')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        filtered = [line for line in out.splitlines() if 'Not an ELF file' in line]
        assert len(filtered) == 1


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_no_soname(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('no-soname.so'), '/lib64/no-soname.so')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'no-soname /lib64/no-soname.so' in out


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_invalid_soname(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('invalid-soname.so'), '/lib64/invalid-soname.so')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'invalid-soname /lib64/invalid-soname.so' in out
        assert 'E: shlib-with-non-pic-code /lib64/invalid-soname.so' not in out


@pytest.mark.skipif(not IS_I686 and (not IS_X86_64 or not HAS_32BIT_GLIBC), reason='i686 glibc only')
def test_non_pic_code_library(binariescheck):
    output, test = binariescheck
    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('non-pic-shared-m32.so'), '/usr/lib/non-pic-shared-m32.so')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'E: shlib-with-non-pic-code' in out


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_no_ldconfig_symlink(binariescheck):
    output, test = binariescheck

    with FakePkg('libfake') as pkg:
        pkgfile = pkg.add_file(get_full_path('libutil-2.29.so'), '/lib64/libutil-2.29.so')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'no-ldconfig-symlink /lib64/libutil-2.29.so' in out
        assert 'E: shlib-policy-name-error SONAME: libutil.so.1 (/lib64/libutil-2.29.so), expected package suffix: 1' in out


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_call_mktemp(binariescheck):
    output, test = binariescheck

    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('call-mktemp'), '/bin/call-mktemp')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'E: call-to-mktemp /bin/call-mktemp' in out


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_call_setgroups(binariescheck):
    output, test = binariescheck

    with FakePkg('fake') as pkg:
        pkgfile = PkgFile('/bin/call-setgroups')
        pkgfile.path = get_full_path('call-setgroups')
        pkg.files[pkgfile.name] = pkgfile
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'E: missing-call-to-setgroups-before-setuid /bin/call-setgroups' in out


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_call_gethostbyname(binariescheck):
    output, test = binariescheck

    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('hostname'), '/usr/bin/hostname')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'W: binary-or-shlib-calls-gethostbyname' in out


def test_bca_files(binariescheck):
    output, test = binariescheck

    with FakePkg('fake') as pkg:
        pkgfile = pkg.add_file(get_full_path('libkleeRuntimeFreeStanding.bca'), '/usr/lib64/klee/runtime/libkleeRuntimeFreeStanding.bca')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'E: ' not in out


@pytest.mark.skipif(not IS_X86_64, reason='x86-64 only')
def test_shlib_policy_name_error(binariescheck):
    output, test = binariescheck

    with FakePkg('libgame') as pkg:
        pkgfile = pkg.add_file(get_full_path('libgame.so'), '/lib64/libgame.so')
        run_elf_checks(test, pkg, pkgfile)
        out = output.print_results(output.results)
        assert 'libgame: E: shlib-policy-name-error SONAME: libgame2-1.9.so.10.0.0 (/lib64/libgame.so), expected package suffix: 1_9-10_0_0' in out
