#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* index.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscis.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isrenumber_ ISRENUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isrenumber_ isrenumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscreatesubis_ ISCREATESUBIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscreatesubis_ iscreatesubis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isclearinfocache_ ISCLEARINFOCACHE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isclearinfocache_ isclearinfocache
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issetinfo_ ISSETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issetinfo_ issetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetinfo_ ISGETINFO
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetinfo_ isgetinfo
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isidentity_ ISIDENTITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isidentity_ isidentity
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issetidentity_ ISSETIDENTITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issetidentity_ issetidentity
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscontiguouslocal_ ISCONTIGUOUSLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscontiguouslocal_ iscontiguouslocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define ispermutation_ ISPERMUTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define ispermutation_ ispermutation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issetpermutation_ ISSETPERMUTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issetpermutation_ issetpermutation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isdestroy_ ISDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isdestroy_ isdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isinvertpermutation_ ISINVERTPERMUTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isinvertpermutation_ isinvertpermutation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetsize_ ISGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetsize_ isgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetlocalsize_ ISGETLOCALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetlocalsize_ isgetlocalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetlayout_ ISGETLAYOUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetlayout_ isgetlayout
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issetlayout_ ISSETLAYOUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issetlayout_ issetlayout
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetminmax_ ISGETMINMAX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetminmax_ isgetminmax
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocate_ ISLOCATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocate_ islocate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetnonlocalis_ ISGETNONLOCALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetnonlocalis_ isgetnonlocalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isrestorenonlocalis_ ISRESTORENONLOCALIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isrestorenonlocalis_ isrestorenonlocalis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isviewfromoptions_ ISVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isviewfromoptions_ isviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isview_ ISVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isview_ isview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isload_ ISLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isload_ isload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issort_ ISSORT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issort_ issort
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issortremovedups_ ISSORTREMOVEDUPS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issortremovedups_ issortremovedups
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define istogeneral_ ISTOGENERAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define istogeneral_ istogeneral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issorted_ ISSORTED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issorted_ issorted
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isduplicate_ ISDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isduplicate_ isduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscopy_ ISCOPY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscopy_ iscopy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isshift_ ISSHIFT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isshift_ isshift
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isoncomm_ ISONCOMM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isoncomm_ isoncomm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issetblocksize_ ISSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issetblocksize_ issetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetblocksize_ ISGETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetblocksize_ isgetblocksize
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  isrenumber_(IS subset,IS subset_mult,PetscInt *N,IS *subset_n, int *ierr)
{
CHKFORTRANNULLOBJECT(subset);
CHKFORTRANNULLOBJECT(subset_mult);
CHKFORTRANNULLINTEGER(N);
PetscBool subset_n_null = !*(void**) subset_n ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subset_n);
*ierr = ISRenumber(
	(IS)PetscToPointer((subset) ),
	(IS)PetscToPointer((subset_mult) ),N,subset_n);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subset_n_null && !*(void**) subset_n) * (void **) subset_n = (void *)-2;
}
PETSC_EXTERN void  iscreatesubis_(IS is,IS comps,IS *subis, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(comps);
PetscBool subis_null = !*(void**) subis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subis);
*ierr = ISCreateSubIS(
	(IS)PetscToPointer((is) ),
	(IS)PetscToPointer((comps) ),subis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subis_null && !*(void**) subis) * (void **) subis = (void *)-2;
}
PETSC_EXTERN void  isclearinfocache_(IS is,PetscBool *clear_permanent_local, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISClearInfoCache(
	(IS)PetscToPointer((is) ),*clear_permanent_local);
}
PETSC_EXTERN void  issetinfo_(IS is,ISInfo *info,ISInfoType *type,PetscBool *permanent,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISSetInfo(
	(IS)PetscToPointer((is) ),*info,*type,*permanent,*flg);
}
PETSC_EXTERN void  isgetinfo_(IS is,ISInfo *info,ISInfoType *type,PetscBool *compute,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISGetInfo(
	(IS)PetscToPointer((is) ),*info,*type,*compute,flg);
}
PETSC_EXTERN void  isidentity_(IS is,PetscBool *ident, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISIdentity(
	(IS)PetscToPointer((is) ),ident);
}
PETSC_EXTERN void  issetidentity_(IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISSetIdentity(
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  iscontiguouslocal_(IS is,PetscInt *gstart,PetscInt *gend,PetscInt *start,PetscBool *contig, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(start);
*ierr = ISContiguousLocal(
	(IS)PetscToPointer((is) ),*gstart,*gend,start,contig);
}
PETSC_EXTERN void  ispermutation_(IS is,PetscBool *perm, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISPermutation(
	(IS)PetscToPointer((is) ),perm);
}
PETSC_EXTERN void  issetpermutation_(IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISSetPermutation(
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  isdestroy_(IS *is, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(is);
 PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = ISDestroy(is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(is);
 }
PETSC_EXTERN void  isinvertpermutation_(IS is,PetscInt *nlocal,IS *isout, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool isout_null = !*(void**) isout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isout);
*ierr = ISInvertPermutation(
	(IS)PetscToPointer((is) ),*nlocal,isout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isout_null && !*(void**) isout) * (void **) isout = (void *)-2;
}
PETSC_EXTERN void  isgetsize_(IS is,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(size);
*ierr = ISGetSize(
	(IS)PetscToPointer((is) ),size);
}
PETSC_EXTERN void  isgetlocalsize_(IS is,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(size);
*ierr = ISGetLocalSize(
	(IS)PetscToPointer((is) ),size);
}
PETSC_EXTERN void  isgetlayout_(IS is,PetscLayout *map, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool map_null = !*(void**) map ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(map);
*ierr = ISGetLayout(
	(IS)PetscToPointer((is) ),map);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! map_null && !*(void**) map) * (void **) map = (void *)-2;
}
PETSC_EXTERN void  issetlayout_(IS is,PetscLayout map, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(map);
*ierr = ISSetLayout(
	(IS)PetscToPointer((is) ),
	(PetscLayout)PetscToPointer((map) ));
}
PETSC_EXTERN void  isgetminmax_(IS is,PetscInt *min,PetscInt *max, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(min);
CHKFORTRANNULLINTEGER(max);
*ierr = ISGetMinMax(
	(IS)PetscToPointer((is) ),min,max);
}
PETSC_EXTERN void  islocate_(IS is,PetscInt *key,PetscInt *location, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(location);
*ierr = ISLocate(
	(IS)PetscToPointer((is) ),*key,location);
}
PETSC_EXTERN void  isgetnonlocalis_(IS is,IS *complement, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool complement_null = !*(void**) complement ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(complement);
*ierr = ISGetNonlocalIS(
	(IS)PetscToPointer((is) ),complement);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! complement_null && !*(void**) complement) * (void **) complement = (void *)-2;
}
PETSC_EXTERN void  isrestorenonlocalis_(IS is,IS *complement, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool complement_null = !*(void**) complement ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(complement);
*ierr = ISRestoreNonlocalIS(
	(IS)PetscToPointer((is) ),complement);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! complement_null && !*(void**) complement) * (void **) complement = (void *)-2;
}
PETSC_EXTERN void  isviewfromoptions_(IS A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = ISViewFromOptions(
	(IS)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  isview_(IS is,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(viewer);
*ierr = ISView(
	(IS)PetscToPointer((is) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  isload_(IS is,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(viewer);
*ierr = ISLoad(
	(IS)PetscToPointer((is) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  issort_(IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISSort(
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  issortremovedups_(IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISSortRemoveDups(
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  istogeneral_(IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISToGeneral(
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  issorted_(IS is,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISSorted(
	(IS)PetscToPointer((is) ),flg);
}
PETSC_EXTERN void  isduplicate_(IS is,IS *newIS, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool newIS_null = !*(void**) newIS ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newIS);
*ierr = ISDuplicate(
	(IS)PetscToPointer((is) ),newIS);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newIS_null && !*(void**) newIS) * (void **) newIS = (void *)-2;
}
PETSC_EXTERN void  iscopy_(IS is,IS isy, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(isy);
*ierr = ISCopy(
	(IS)PetscToPointer((is) ),
	(IS)PetscToPointer((isy) ));
}
PETSC_EXTERN void  isshift_(IS is,PetscInt *offset,IS isy, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLOBJECT(isy);
*ierr = ISShift(
	(IS)PetscToPointer((is) ),*offset,
	(IS)PetscToPointer((isy) ));
}
PETSC_EXTERN void  isoncomm_(IS is,MPI_Fint * comm,PetscCopyMode *mode,IS *newis, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool newis_null = !*(void**) newis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newis);
*ierr = ISOnComm(
	(IS)PetscToPointer((is) ),
	MPI_Comm_f2c(*(comm)),*mode,newis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newis_null && !*(void**) newis) * (void **) newis = (void *)-2;
}
PETSC_EXTERN void  issetblocksize_(IS is,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
*ierr = ISSetBlockSize(
	(IS)PetscToPointer((is) ),*bs);
}
PETSC_EXTERN void  isgetblocksize_(IS is,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
CHKFORTRANNULLINTEGER(size);
*ierr = ISGetBlockSize(
	(IS)PetscToPointer((is) ),size);
}
#if defined(__cplusplus)
}
#endif
