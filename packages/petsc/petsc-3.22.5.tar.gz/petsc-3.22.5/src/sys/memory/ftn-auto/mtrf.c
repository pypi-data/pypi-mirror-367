#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* mtr.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocgetcurrentusage_ PETSCMALLOCGETCURRENTUSAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocgetcurrentusage_ petscmallocgetcurrentusage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocgetmaximumusage_ PETSCMALLOCGETMAXIMUMUSAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocgetmaximumusage_ petscmallocgetmaximumusage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocpushmaximumusage_ PETSCMALLOCPUSHMAXIMUMUSAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocpushmaximumusage_ petscmallocpushmaximumusage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocpopmaximumusage_ PETSCMALLOCPOPMAXIMUMUSAGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocpopmaximumusage_ petscmallocpopmaximumusage
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocviewset_ PETSCMALLOCVIEWSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocviewset_ petscmallocviewset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocviewget_ PETSCMALLOCVIEWGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocviewget_ petscmallocviewget
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmalloctraceset_ PETSCMALLOCTRACESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmalloctraceset_ petscmalloctraceset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmalloctraceget_ PETSCMALLOCTRACEGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmalloctraceget_ petscmalloctraceget
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocsetdebug_ PETSCMALLOCSETDEBUG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocsetdebug_ petscmallocsetdebug
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmallocgetdebug_ PETSCMALLOCGETDEBUG
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmallocgetdebug_ petscmallocgetdebug
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmalloclogrequestedsizeset_ PETSCMALLOCLOGREQUESTEDSIZESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmalloclogrequestedsizeset_ petscmalloclogrequestedsizeset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmalloclogrequestedsizeget_ PETSCMALLOCLOGREQUESTEDSIZEGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmalloclogrequestedsizeget_ petscmalloclogrequestedsizeget
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscmallocgetcurrentusage_(PetscLogDouble *space, int *ierr)
{
*ierr = PetscMallocGetCurrentUsage(space);
}
PETSC_EXTERN void  petscmallocgetmaximumusage_(PetscLogDouble *space, int *ierr)
{
*ierr = PetscMallocGetMaximumUsage(space);
}
PETSC_EXTERN void  petscmallocpushmaximumusage_(int *event, int *ierr)
{
*ierr = PetscMallocPushMaximumUsage(*event);
}
PETSC_EXTERN void  petscmallocpopmaximumusage_(int *event,PetscLogDouble *mu, int *ierr)
{
*ierr = PetscMallocPopMaximumUsage(*event,mu);
}
PETSC_EXTERN void  petscmallocviewset_(PetscLogDouble *logmin, int *ierr)
{
*ierr = PetscMallocViewSet(*logmin);
}
PETSC_EXTERN void  petscmallocviewget_(PetscBool *logging, int *ierr)
{
*ierr = PetscMallocViewGet(logging);
}
PETSC_EXTERN void  petscmalloctraceset_(PetscViewer viewer,PetscBool *active,PetscLogDouble *logmin, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscMallocTraceSet(PetscPatchDefaultViewers((PetscViewer*)viewer),*active,*logmin);
}
PETSC_EXTERN void  petscmalloctraceget_(PetscBool *logging, int *ierr)
{
*ierr = PetscMallocTraceGet(logging);
}
PETSC_EXTERN void  petscmallocsetdebug_(PetscBool *eachcall,PetscBool *initializenan, int *ierr)
{
*ierr = PetscMallocSetDebug(*eachcall,*initializenan);
}
PETSC_EXTERN void  petscmallocgetdebug_(PetscBool *basic,PetscBool *eachcall,PetscBool *initializenan, int *ierr)
{
*ierr = PetscMallocGetDebug(basic,eachcall,initializenan);
}
PETSC_EXTERN void  petscmalloclogrequestedsizeset_(PetscBool *flg, int *ierr)
{
*ierr = PetscMallocLogRequestedSizeSet(*flg);
}
PETSC_EXTERN void  petscmalloclogrequestedsizeget_(PetscBool *flg, int *ierr)
{
*ierr = PetscMallocLogRequestedSizeGet(flg);
}
#if defined(__cplusplus)
}
#endif
