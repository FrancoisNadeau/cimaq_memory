
# def force_utf8(inpt: Union[bytes, str, os.PathLike],
#                encoding: str = None) -> bytes:
#     inpt = get_bytes(inpt)
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     return (
#         inpt.replace("\0xff".encode(encoding), "".encode(encoding))
#         .replace("0xf8".encode(encoding), "".encode(encoding))
#         .replace("\x00".encode(encoding), "".encode(encoding))
#         .replace("x0".encode(encoding), "".encode(encoding))
#         .decode("utf8", "replace")
#         .replace("�", "")
#         .strip()
#         .encode("utf8")
#     )

# def force_ascii(astring: str) -> str:
#     """
#     Source: https://stackoverflow.com/questions/8689795/how-can-i-remove-non-ascii-characters-but-leave-periods-and-spaces-using-python
#     """
#     return "".join(filter(lambda x: x in set(string.printable), astring))

# def get_dupvalues(
#     inpt: Union[bytes, str, os.PathLike],
#     encoding: str = None,
#     hdr: bool = None,
#     delimiter: bytes = None,
# ) -> list:
#     inpt = get_bytes(inpt)
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     hdr = [hdr if hdr != None else get_has_header(inpt, encoding)][0]
#     bytelines = [inpt.splitlines() if not hdr else inpt.splitlines()[1:]][0]
#     ev_itms, od_itms = evenodd([line.split(delimiter) for line in bytelines])
#     checkup = tuple(zip(list(df(ev_itms).iteritems()), list(df(od_itms).iteritems())))
#     try:
#         return [itm[0][1].all() == itm[1][1].all() for itm in checkup]
#     except IndexError:
#         return False

# def fforce_utf8(inpt: Union[bytes, str, os.PathLike],
#                 encoding: str = None) -> bytes:
#     inpt = get_bytes(inpt)
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     return b'\n'.join([b'\t'.join([chr(int.from_bytes(
#                item, sys.byteorder)).encode()
#                for item in list(line) if
#                chr(int.from_bytes(item, sys.byteorder)) != '\x00']
#             for line in inpt.splitlines())])

# def ensure_bencod(inpt: bytes, encoding: str = None) -> bytes:
#     return inpt.decode(encoding, 'replace').replace('�', '').encode(encoding)

# def get_nullrep1(inpt: bytes, encoding: str = None) -> bytes:
#     ''' Returns null byte representation as bytes in native file encoding'''
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     return bytes([inpt.splitlines(keepends = True)[-1][-1]]).decode(encoding).encode(encoding)
#     rep = chr(list(inpt)[-1]).encode(encoding)
#     return Counter([chr(itm) for itm in
#                     list(chr(list(inpt.splitlines()[-1])[-1]).encode(
#                         encoding))]).most_common(1)[0][0]

# def get_nullrep(inpt, encoding: str = None) -> bytes:
#     return [itm for itm in list(inpt) if
#             chr(int.from_bytes(itm, sys.byteorder)).encode(
#                 encoding) == "\x00".encode(encoding)]

# def strip_null(inpt: bytes, encoding: str = None) -> bytes:
#     """ Remove null bytes from byte stream with proper representation
#         Adapted from:
#         https://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3
#         All files end by a null byte, so the last byte in a file shows
#         how null bytes are represented within this file 
        
#         Parameters
#         ----------
#         inpt: Bytes stream from buffer or file
#                 - See help(snif.get_bytes)
                
#         - Optional
#           --------
#         encoding: Character encoding of the bytes in buffer
#     """
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     try:
#         return inpt.replace(chr(int.from_bytes(
#                    b"\x00", sys.byteorder)).encode(encoding), ''.encode(encoding))
#     except AttributeError:
#         return inpt.replace(get_nullrep(inpt, encoding), ''.encode(encoding))

# def mkfrombytes(inpt: Union[bytes, str, os.PathLike],
#                 encoding: str = None,
#                 delimiter: bytes = None,
#                 hdr: bool = False,
#                 dup_index: bool = None,
#                 new_sep: bytes = b"\t") -> bytes:
#     inpt = get_bytes(inpt)
#     encoding = [encoding if encoding
#                 else get_bencod(inpt)][0]
#     delimiter = [delimiter if delimiter
#                  else get_delimiter(inpt)][0]
#     hdr = [hdr if hdr else get_has_header(inpt)][0]
#     dup_index = [dup_index if dup_index
#                 else get_dup_index(inpt)][0]
#     if not dup_index:
#         try:
#             return (
#                 b"\n".join(
#                     [
#                         re.sub(
#                             b"\s{2,}",
#                             new_sep,
#                             re.sub(
#                                 delimiter,
#                                 new_sep,
#                                 re.sub(
#                                     delimiter + b"{2,}",
#                                     delimiter + b"NaN" + delimiter, line
#                                 ),
#                             ),
#                         )
#                         .strip()
#                         .replace(b" ", b"_")
#                         .replace(b"\x00", b"NaN")
#                         for line in force_utf8(strip_null(inpt, encoding), encoding).splitlines()
#                     ]
#                 )
#                 .replace(delimiter, new_sep)
#                 .decode()
#                 .encode()
#             )
#         except:
#             return strip_null(inpt, encoding)
#     else:
#         return force_utf8(strip_null(fix_dup_index(inpt,
#                                                    encoding, hdr, delimiter),
#                                      encoding), encoding)

# def fix_dup_index(
#     inpt: Union[bytes, str, os.PathLike],
#     encoding: str = None,
#     hdr: bool = False,
#     delimiter: bytes = None,
# ) -> bytes:
#     inpt = get_bytes(inpt)
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     tmp = evenodd(force_utf8(inpt).splitlines())

#     evdf = df([line.decode().split() for line in tmp[0]])
#     oddf = df([line.decode().split() for line in tmp[1]])

#     booltest = [
#         col for col in evdf.columns if evdf[col].values.all() == oddf[col].values.all()
#     ]
#     newsheet = pd.merge(evdf, oddf, on=booltest)
#     return "\\n".join(
#         [
#             "\t".join([itm for itm in line])
#             for line in newsheet.rename(
#                 dict(enumerate(newsheet.columns))
#             ).values.tolist()
#         ]
#     ).encode()

# def fix_dup_index(
#     inpt: Union[bytes, str, os.PathLike],
#     encoding: str = None,
#     hdr: bool = False,
#     delimiter: bytes = None,
#     nfields: int = None
# ) -> bytes:
#     inpt = get_bytes(inpt)
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     nfields = [nfields if nfields else get_nfields(inpt, hdr)]
#     evdf, oddf = (df(line.split() for line in lines) for lines
#                   in evenodd(inpt.splitlines()))
#     booltest = [itm[0] for itm in enumerate(
#                    tuple(zip([itm[1] for itm in
#                               evdf.iteritems()],
#                               [itm[1] for itm in
#                                oddf.iteritems()])))
#                 if all(itm[1][0].values == itm[1][1].values)]
#     return b'\n'.join(b'\t'.join([itm for itm in row[1]]) for row in
#                       pd.concat((evdf[booltest],
#                        pd.Series([b'non']*evdf.shape[1]),
# #                       pd.Series((int(len(row[1].values)) \
# #                                  == nfields[0] -1)
# #                                 for row in evdf.iterrows()),
#                        oddf[booltest[-1]:]), axis = 1).iterrows())

#  if type(itm) == bytes else bytearray(struct.pack("f", itm))
# 
#.tostring().encode()
#     return b'\n'.join(b'\t'.join(itm for
#                                  itm in row[1].values.tolist())
#                       for row in datas.iterrows())



# def fix_na_reps(inpt: bytes,
#                 encoding: str = None,
#                 delimiter: bytes = None) - > bytes:
#     inpt = get_bytes(inpt)
#     encoding = [encoding if encoding else get_bencod(inpt)][0]
#     delimiter = [delimiter if delimiter else get_delimiter(inpt, encoding)][0]    
#     return '\n'.encode(encoding).join(re.sub(delimiter+'{2,}'.encode(encoding),
#                       delimiter+str(np.nan).encode(encoding)+delimiter,
#                       line) for line in inpt.splitlines())

######## For ZipFile archives ########################################



# def getnametuple(myzip):
#     """
#     Adjustment to ZipFile.namelist() function to prevent MAC-exclusive
#     '__MACOSX' and '.DS_Store' files from interfering.
#     Only necessary for files compressed with OS 10.3 or earlier.
#     Source: https://superuser.com/questions/104500/what-is-macosx-folder
#     Command line solution:
#         ``` zip -r dir.zip . -x ".*" -x "__MACOSX"
#     Source: https://apple.stackexchange.com/questions/239578/compress-without-ds-store-and-macosx
#     """
#     return tuple(
#         sorted(
#             list(
#                 itm
#                 for itm in myzip.namelist()
#                 if bname(itm).startswith(".") == False
#                 and "__MACOSX" not in itm
#                 and "textClipping" not in itm
#                 and itm != os.path.splitext(bname(dname(itm)))[0] + "/"
#             )
#         )
#     )


# def get_zip_contents(
#     archv_path: Union[os.PathLike, str],
#     ntpl: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     to_close: bool = True,
# ) -> object:
#     myzip = ZipFile(archv_path)
#     ntpl = [ntpl if ntpl else getnametuple(myzip)][0]

#     vals = (
#         df(
#             tuple(
#                 dict(zip(evenodd(itm)[0], evenodd(itm)[1]))
#                 for itm in tuple(
#                     tuple(
#                         force_ascii(repr(itm.lower()))
#                         .strip()
#                         .replace("'", "")
#                         .replace("'", "")
#                         .replace("=", " ")[:-2]
#                         .split()
#                     )[1:]
#                     for itm in set(
#                         repr(myzip.getinfo(itm))
#                         .strip(" ")
#                         .replace(itm, itm.replace(" ", "_"))
#                         if " " in itm
#                         else repr(myzip.getinfo(itm)).strip(" ")
#                         for itm in ntpl
#                     )
#                 )
#             ),
#             dtype="object",
#         )
#         .sort_values("filename")
#         .reset_index(drop=True)
#     )
#     vals[["src_name", "ext"]] = [(nm, os.path.splitext(nm)[1]) for nm in ntpl]
#     vals["filename"] = [
#         "_".join(
#             pd.Series(
#                 row[1].filename.lower().replace("/",
#                                                 "_").replace("-",
#                                                              "_").split("_")
#             ).unique()
#             .__iter__()
#         )
#         for row in vals.iterrows()
#     ]
#     if exclude:
#         vals = vals.drop(
#             [
#                 row[0]
#                 for row in vals.iterrows()
#                 if row[1].filename
#                 not in filter_lst_exc(exclude, [itm.lower() for itm in vals.filename])
#             ],
#             axis=0,
#         )
#     if to_close:
#         myzip.close()
#         return vals
#     else:
#         return (myzip, vals)


# def scan_zip_contents(
#     archv_path: Union[os.PathLike, str],
#     ntpl: Union[str, list, tuple] = [],
#     to_xtrct: Union[str, list, tuple] = [],
#     exclude: Union[str, list, tuple] = [],
#     to_close: bool = True,
#     withbytes: bool = False,
#     dst_path: Union[os.PathLike, str] = None,
# ) -> object:

#     myzip, vals = get_zip_contents(archv_path, ntpl, exclude, to_close=False)
#     if exclude:
#         vals = vals.drop(
#             [
#                 row[0]
#                 for row in vals.iterrows()
#                 if row[1].filename
#                 not in filter_lst_exc(exclude, [itm.lower() for itm in vals.filename])
#             ],
#             axis=0,
#         )
#     if to_xtrct:
#         dst_path = [
#             dst_path
#             if dst_path
#             else pjoin(dname(archv_path), os.path.splitext(bname(archv_path))[0])
#         ][0]
#         os.makedirs(dst_path, exist_ok=True)
#         xtrct_lst = vals.loc[
#             [
#                 row[0]
#                 for row in vals.iterrows()
#                 if row[1].filename
#                 in filter_lst_inc(to_xtrct, list(vals.filename), sort=True)
#             ]
#         ]
#         [
#             shutil.move(
#                 myzip.extract(member=row[1].src_name, path=dst_path),
#                 pjoin(
#                     dst_path,
#                     "_".join(
#                         pd.Series(
#                             row[1].filename.lower().replace("-", "_").split("_")
#                         ).unique()
#                     ),
#                 ),
#             )
#             for row in tqdm(xtrct_lst.iterrows(), desc="extracting")
#         ]
#         vals = vals.loc[
#             [
#                 row[0]
#                 for row in vals.iterrows()
#                 if row[1].filename not in xtrct_lst.values
#             ]
#         ]
#         removeEmptyFolders(dst_path, False)
#     if withbytes:
#         vals["bsheets"] = [
#             myzip.open(row[1].src_name).read().lower() for row in vals.iterrows()
#         ]
#     if to_close:
#         myzip.close()
#     return vals.reset_index(drop=True)



