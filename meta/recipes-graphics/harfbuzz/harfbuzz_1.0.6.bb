SUMMARY = "Text shaping library"
DESCRIPTION = "HarfBuzz is an OpenType text shaping engine."
HOMEPAGE = "http://www.freedesktop.org/wiki/Software/HarfBuzz"
BUGTRACKER = "https://bugs.freedesktop.org/enter_bug.cgi?product=HarfBuzz"

LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://COPYING;md5=e021dd6dda6ff1e6b1044002fc662b9b \
                    file://src/hb-ucdn/COPYING;md5=994ba0f1295f15b4bda4999a5bbeddef \
"

SECTION = "libs"

SRC_URI = "http://www.freedesktop.org/software/harfbuzz/release/${BP}.tar.bz2"
SRC_URI[md5sum] = "2256fd144c936936db9c92e77510a011"
SRC_URI[sha256sum] = "f616a7fbdc78a627043f9029000bf08c0c71df59cde4143fc92a014f6a993b26"

inherit autotools pkgconfig lib_package

DEPENDS = "glib-2.0 cairo freetype"

BBCLASSEXTEND = "native"

EXTRA_OECONF = "--with-glib --with-freetype --with-cairo --without-graphite2"

PACKAGECONFIG ??= "icu"
PACKAGECONFIG[icu] = "--with-icu,--without-icu,icu"

PACKAGES =+ "${PN}-icu ${PN}-icu-dbg ${PN}-icu-dev"

FILES_${PN}-icu = "${libdir}/libharfbuzz-icu.so.*"
FILES_${PN}-icu-dbg = "${libdir}/.debug/libharfbuzz-icu.so*"
FILES_${PN}-icu-dev = "${libdir}/libharfbuzz-icu.la \
                       ${libdir}/libharfbuzz-icu.so \
                       ${libdir}/pkgconfig/harfbuzz-icu.pc \
"
