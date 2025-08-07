#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* iscoloring.c */
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
#define iscoloringsettype_ ISCOLORINGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscoloringsettype_ iscoloringsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscoloringgettype_ ISCOLORINGGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscoloringgettype_ iscoloringgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscoloringdestroy_ ISCOLORINGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscoloringdestroy_ iscoloringdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscoloringviewfromoptions_ ISCOLORINGVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscoloringviewfromoptions_ iscoloringviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscoloringview_ ISCOLORINGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscoloringview_ iscoloringview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscoloringcreate_ ISCOLORINGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscoloringcreate_ iscoloringcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isbuildtwosided_ ISBUILDTWOSIDED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isbuildtwosided_ isbuildtwosided
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define ispartitioningtonumbering_ ISPARTITIONINGTONUMBERING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define ispartitioningtonumbering_ ispartitioningtonumbering
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define ispartitioningcount_ ISPARTITIONINGCOUNT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define ispartitioningcount_ ispartitioningcount
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isallgather_ ISALLGATHER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isallgather_ isallgather
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define iscomplement_ ISCOMPLEMENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define iscomplement_ iscomplement
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  iscoloringsettype_(ISColoring coloring,ISColoringType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(coloring);
*ierr = ISColoringSetType(
	(ISColoring)PetscToPointer((coloring) ),*type);
}
PETSC_EXTERN void  iscoloringgettype_(ISColoring coloring,ISColoringType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(coloring);
*ierr = ISColoringGetType(
	(ISColoring)PetscToPointer((coloring) ),type);
}
PETSC_EXTERN void  iscoloringdestroy_(ISColoring *iscoloring, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(iscoloring);
 PetscBool iscoloring_null = !*(void**) iscoloring ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(iscoloring);
*ierr = ISColoringDestroy(iscoloring);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! iscoloring_null && !*(void**) iscoloring) * (void **) iscoloring = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(iscoloring);
 }
PETSC_EXTERN void  iscoloringviewfromoptions_(ISColoring obj,PetscObject bobj, char optionname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLOBJECT(bobj);
/* insert Fortran-to-C conversion for optionname */
  FIXCHAR(optionname,cl0,_cltmp0);
*ierr = ISColoringViewFromOptions(
	(ISColoring)PetscToPointer((obj) ),
	(PetscObject)PetscToPointer((bobj) ),_cltmp0);
  FREECHAR(optionname,_cltmp0);
}
PETSC_EXTERN void  iscoloringview_(ISColoring iscoloring,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(iscoloring);
CHKFORTRANNULLOBJECT(viewer);
*ierr = ISColoringView(
	(ISColoring)PetscToPointer((iscoloring) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  iscoloringcreate_(MPI_Fint * comm,PetscInt *ncolors,PetscInt *n, ISColoringValue colors[],PetscCopyMode *mode,ISColoring *iscoloring, int *ierr)
{
PetscBool iscoloring_null = !*(void**) iscoloring ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(iscoloring);
*ierr = ISColoringCreate(
	MPI_Comm_f2c(*(comm)),*ncolors,*n,
	(ISColoringValue* )PetscToPointer((colors) ),*mode,iscoloring);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! iscoloring_null && !*(void**) iscoloring) * (void **) iscoloring = (void *)-2;
}
PETSC_EXTERN void  isbuildtwosided_(IS ito,IS toindx,IS *rows, int *ierr)
{
CHKFORTRANNULLOBJECT(ito);
CHKFORTRANNULLOBJECT(toindx);
PetscBool rows_null = !*(void**) rows ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rows);
*ierr = ISBuildTwoSided(
	(IS)PetscToPointer((ito) ),
	(IS)PetscToPointer((toindx) ),rows);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rows_null && !*(void**) rows) * (void **) rows = (void *)-2;
}
PETSC_EXTERN void  ispartitioningtonumbering_(IS part,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = ISPartitioningToNumbering(
	(IS)PetscToPointer((part) ),is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  ispartitioningcount_(IS part,PetscInt *len,PetscInt count[], int *ierr)
{
CHKFORTRANNULLOBJECT(part);
CHKFORTRANNULLINTEGER(count);
*ierr = ISPartitioningCount(
	(IS)PetscToPointer((part) ),*len,count);
}
PETSC_EXTERN void  isallgather_(IS is,IS *isout, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool isout_null = !*(void**) isout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isout);
*ierr = ISAllGather(
	(IS)PetscToPointer((is) ),isout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isout_null && !*(void**) isout) * (void **) isout = (void *)-2;
}
PETSC_EXTERN void  iscomplement_(IS is,PetscInt *nmin,PetscInt *nmax,IS *isout, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool isout_null = !*(void**) isout ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isout);
*ierr = ISComplement(
	(IS)PetscToPointer((is) ),*nmin,*nmax,isout);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isout_null && !*(void**) isout) * (void **) isout = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
