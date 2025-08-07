#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pmap.c */
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
#define petsclayoutcreate_ PETSCLAYOUTCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutcreate_ petsclayoutcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutcreatefromsizes_ PETSCLAYOUTCREATEFROMSIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutcreatefromsizes_ petsclayoutcreatefromsizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutdestroy_ PETSCLAYOUTDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutdestroy_ petsclayoutdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutcreatefromranges_ PETSCLAYOUTCREATEFROMRANGES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutcreatefromranges_ petsclayoutcreatefromranges
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutsetup_ PETSCLAYOUTSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutsetup_ petsclayoutsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutduplicate_ PETSCLAYOUTDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutduplicate_ petsclayoutduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutreference_ PETSCLAYOUTREFERENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutreference_ petsclayoutreference
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutsetislocaltoglobalmapping_ PETSCLAYOUTSETISLOCALTOGLOBALMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutsetislocaltoglobalmapping_ petsclayoutsetislocaltoglobalmapping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutsetlocalsize_ PETSCLAYOUTSETLOCALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutsetlocalsize_ petsclayoutsetlocalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutgetlocalsize_ PETSCLAYOUTGETLOCALSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutgetlocalsize_ petsclayoutgetlocalsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutsetsize_ PETSCLAYOUTSETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutsetsize_ petsclayoutsetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutgetsize_ PETSCLAYOUTGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutgetsize_ petsclayoutgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutsetblocksize_ PETSCLAYOUTSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutsetblocksize_ petsclayoutsetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutgetblocksize_ PETSCLAYOUTGETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutgetblocksize_ petsclayoutgetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutgetrange_ PETSCLAYOUTGETRANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutgetrange_ petsclayoutgetrange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutcompare_ PETSCLAYOUTCOMPARE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutcompare_ petsclayoutcompare
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutfindowner_ PETSCLAYOUTFINDOWNER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutfindowner_ petsclayoutfindowner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclayoutfindownerindex_ PETSCLAYOUTFINDOWNERINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclayoutfindownerindex_ petsclayoutfindownerindex
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petsclayoutcreate_(MPI_Fint * comm,PetscLayout *map, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(map);
 PetscBool map_null = !*(void**) map ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutCreate(
	MPI_Comm_f2c(*(comm)),map);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! map_null && !*(void**) map) * (void **) map = (void *)-2;
}
PETSC_EXTERN void  petsclayoutcreatefromsizes_(MPI_Fint * comm,PetscInt *n,PetscInt *N,PetscInt *bs,PetscLayout *map, int *ierr)
{
PetscBool map_null = !*(void**) map ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutCreateFromSizes(
	MPI_Comm_f2c(*(comm)),*n,*N,*bs,map);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! map_null && !*(void**) map) * (void **) map = (void *)-2;
}
PETSC_EXTERN void  petsclayoutdestroy_(PetscLayout *map, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(map);
 PetscBool map_null = !*(void**) map ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutDestroy(map);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! map_null && !*(void**) map) * (void **) map = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(map);
 }
PETSC_EXTERN void  petsclayoutcreatefromranges_(MPI_Fint * comm, PetscInt range[],PetscCopyMode *mode,PetscInt *bs,PetscLayout *newmap, int *ierr)
{
CHKFORTRANNULLINTEGER(range);
PetscBool newmap_null = !*(void**) newmap ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newmap);
*ierr = PetscLayoutCreateFromRanges(
	MPI_Comm_f2c(*(comm)),range,*mode,*bs,newmap);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newmap_null && !*(void**) newmap) * (void **) newmap = (void *)-2;
}
PETSC_EXTERN void  petsclayoutsetup_(PetscLayout map, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutSetUp(
	(PetscLayout)PetscToPointer((map) ));
}
PETSC_EXTERN void  petsclayoutduplicate_(PetscLayout in,PetscLayout *out, int *ierr)
{
CHKFORTRANNULLOBJECT(in);
PetscBool out_null = !*(void**) out ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(out);
*ierr = PetscLayoutDuplicate(
	(PetscLayout)PetscToPointer((in) ),out);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! out_null && !*(void**) out) * (void **) out = (void *)-2;
}
PETSC_EXTERN void  petsclayoutreference_(PetscLayout in,PetscLayout *out, int *ierr)
{
CHKFORTRANNULLOBJECT(in);
PetscBool out_null = !*(void**) out ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(out);
*ierr = PetscLayoutReference(
	(PetscLayout)PetscToPointer((in) ),out);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! out_null && !*(void**) out) * (void **) out = (void *)-2;
}
PETSC_EXTERN void  petsclayoutsetislocaltoglobalmapping_(PetscLayout in,ISLocalToGlobalMapping ltog, int *ierr)
{
CHKFORTRANNULLOBJECT(in);
CHKFORTRANNULLOBJECT(ltog);
*ierr = PetscLayoutSetISLocalToGlobalMapping(
	(PetscLayout)PetscToPointer((in) ),
	(ISLocalToGlobalMapping)PetscToPointer((ltog) ));
}
PETSC_EXTERN void  petsclayoutsetlocalsize_(PetscLayout map,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutSetLocalSize(
	(PetscLayout)PetscToPointer((map) ),*n);
}
PETSC_EXTERN void  petsclayoutgetlocalsize_(PetscLayout map,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
CHKFORTRANNULLINTEGER(n);
*ierr = PetscLayoutGetLocalSize(
	(PetscLayout)PetscToPointer((map) ),n);
}
PETSC_EXTERN void  petsclayoutsetsize_(PetscLayout map,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutSetSize(
	(PetscLayout)PetscToPointer((map) ),*n);
}
PETSC_EXTERN void  petsclayoutgetsize_(PetscLayout map,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
CHKFORTRANNULLINTEGER(n);
*ierr = PetscLayoutGetSize(
	(PetscLayout)PetscToPointer((map) ),n);
}
PETSC_EXTERN void  petsclayoutsetblocksize_(PetscLayout map,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutSetBlockSize(
	(PetscLayout)PetscToPointer((map) ),*bs);
}
PETSC_EXTERN void  petsclayoutgetblocksize_(PetscLayout map,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
CHKFORTRANNULLINTEGER(bs);
*ierr = PetscLayoutGetBlockSize(
	(PetscLayout)PetscToPointer((map) ),bs);
}
PETSC_EXTERN void  petsclayoutgetrange_(PetscLayout map,PetscInt *rstart,PetscInt *rend, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
CHKFORTRANNULLINTEGER(rstart);
CHKFORTRANNULLINTEGER(rend);
*ierr = PetscLayoutGetRange(
	(PetscLayout)PetscToPointer((map) ),rstart,rend);
}
PETSC_EXTERN void  petsclayoutcompare_(PetscLayout mapa,PetscLayout mapb,PetscBool *congruent, int *ierr)
{
CHKFORTRANNULLOBJECT(mapa);
CHKFORTRANNULLOBJECT(mapb);
*ierr = PetscLayoutCompare(
	(PetscLayout)PetscToPointer((mapa) ),
	(PetscLayout)PetscToPointer((mapb) ),congruent);
}
PETSC_EXTERN void  petsclayoutfindowner_(PetscLayout map,PetscInt *idx,PetscMPIInt *owner, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
*ierr = PetscLayoutFindOwner(
	(PetscLayout)PetscToPointer((map) ),*idx,owner);
}
PETSC_EXTERN void  petsclayoutfindownerindex_(PetscLayout map,PetscInt *idx,PetscMPIInt *owner,PetscInt *lidx, int *ierr)
{
CHKFORTRANNULLOBJECT(map);
CHKFORTRANNULLINTEGER(lidx);
*ierr = PetscLayoutFindOwnerIndex(
	(PetscLayout)PetscToPointer((map) ),*idx,owner,lidx);
}
#if defined(__cplusplus)
}
#endif
