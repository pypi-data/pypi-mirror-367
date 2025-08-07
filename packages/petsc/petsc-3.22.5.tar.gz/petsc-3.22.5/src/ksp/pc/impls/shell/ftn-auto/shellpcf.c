#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* shellpc.c */
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

#include "petscpc.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcshellsetcontext_ PCSHELLSETCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcshellsetcontext_ pcshellsetcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcshellsetname_ PCSHELLSETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcshellsetname_ pcshellsetname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcshellgetname_ PCSHELLGETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcshellgetname_ pcshellgetname
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcshellsetcontext_(PC pc,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCShellSetContext(
	(PC)PetscToPointer((pc) ),ctx);
}
PETSC_EXTERN void  pcshellsetname_(PC pc, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PCShellSetName(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  pcshellgetname_(PC pc, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCShellGetName(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
#if defined(__cplusplus)
}
#endif
