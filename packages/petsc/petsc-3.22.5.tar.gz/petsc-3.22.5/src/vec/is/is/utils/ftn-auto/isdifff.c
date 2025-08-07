#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* isdiff.c */
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
#define isdifference_ ISDIFFERENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isdifference_ isdifference
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issum_ ISSUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issum_ issum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isexpand_ ISEXPAND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isexpand_ isexpand
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isintersect_ ISINTERSECT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isintersect_ isintersect
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isconcatenate_ ISCONCATENATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isconcatenate_ isconcatenate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islisttopair_ ISLISTTOPAIR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islisttopair_ islisttopair
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isembed_ ISEMBED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isembed_ isembed
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define issortpermutation_ ISSORTPERMUTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define issortpermutation_ issortpermutation
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  isdifference_(IS is1,IS is2,IS *isout, int *ierr)
{
CHKFORTRANNULLOBJECT(is1);
CHKFORTRANNULLOBJECT(is2);
PetscBool isout_null = !*(void**) isout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isout);
*ierr = ISDifference(
	(IS)PetscToPointer((is1) ),
	(IS)PetscToPointer((is2) ),isout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isout_null && !*(void**) isout) * (void **) isout = (void *)-2;
}
PETSC_EXTERN void  issum_(IS is1,IS is2,IS *is3, int *ierr)
{
CHKFORTRANNULLOBJECT(is1);
CHKFORTRANNULLOBJECT(is2);
PetscBool is3_null = !*(void**) is3 ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is3);
*ierr = ISSum(
	(IS)PetscToPointer((is1) ),
	(IS)PetscToPointer((is2) ),is3);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is3_null && !*(void**) is3) * (void **) is3 = (void *)-2;
}
PETSC_EXTERN void  isexpand_(IS is1,IS is2,IS *isout, int *ierr)
{
CHKFORTRANNULLOBJECT(is1);
CHKFORTRANNULLOBJECT(is2);
PetscBool isout_null = !*(void**) isout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isout);
*ierr = ISExpand(
	(IS)PetscToPointer((is1) ),
	(IS)PetscToPointer((is2) ),isout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isout_null && !*(void**) isout) * (void **) isout = (void *)-2;
}
PETSC_EXTERN void  isintersect_(IS is1,IS is2,IS *isout, int *ierr)
{
CHKFORTRANNULLOBJECT(is1);
CHKFORTRANNULLOBJECT(is2);
PetscBool isout_null = !*(void**) isout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isout);
*ierr = ISIntersect(
	(IS)PetscToPointer((is1) ),
	(IS)PetscToPointer((is2) ),isout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isout_null && !*(void**) isout) * (void **) isout = (void *)-2;
}
PETSC_EXTERN void  isconcatenate_(MPI_Fint * comm,PetscInt *len, IS islist[],IS *isout, int *ierr)
{
PetscBool islist_null = !*(void**) islist ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(islist);
PetscBool isout_null = !*(void**) isout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isout);
*ierr = ISConcatenate(
	MPI_Comm_f2c(*(comm)),*len,islist,isout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! islist_null && !*(void**) islist) * (void **) islist = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isout_null && !*(void**) isout) * (void **) isout = (void *)-2;
}
PETSC_EXTERN void  islisttopair_(MPI_Fint * comm,PetscInt *listlen,IS islist[],IS *xis,IS *yis, int *ierr)
{
PetscBool islist_null = !*(void**) islist ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(islist);
PetscBool xis_null = !*(void**) xis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(xis);
PetscBool yis_null = !*(void**) yis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(yis);
*ierr = ISListToPair(
	MPI_Comm_f2c(*(comm)),*listlen,islist,xis,yis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! islist_null && !*(void**) islist) * (void **) islist = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! xis_null && !*(void**) xis) * (void **) xis = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! yis_null && !*(void**) yis) * (void **) yis = (void *)-2;
}
PETSC_EXTERN void  isembed_(IS a,IS b,PetscBool *drop,IS *c, int *ierr)
{
CHKFORTRANNULLOBJECT(a);
CHKFORTRANNULLOBJECT(b);
PetscBool c_null = !*(void**) c ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(c);
*ierr = ISEmbed(
	(IS)PetscToPointer((a) ),
	(IS)PetscToPointer((b) ),*drop,c);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! c_null && !*(void**) c) * (void **) c = (void *)-2;
}
PETSC_EXTERN void  issortpermutation_(IS f,PetscBool *always,IS *h, int *ierr)
{
CHKFORTRANNULLOBJECT(f);
PetscBool h_null = !*(void**) h ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(h);
*ierr = ISSortPermutation(
	(IS)PetscToPointer((f) ),*always,h);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! h_null && !*(void**) h) * (void **) h = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
