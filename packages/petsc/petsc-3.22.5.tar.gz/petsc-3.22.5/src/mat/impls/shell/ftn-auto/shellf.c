#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* shell.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matshellgetcontext_ MATSHELLGETCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matshellgetcontext_ matshellgetcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matshellsetcontext_ MATSHELLSETCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matshellsetcontext_ matshellsetcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matshellsetmanagescalingshifts_ MATSHELLSETMANAGESCALINGSHIFTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matshellsetmanagescalingshifts_ matshellsetmanagescalingshifts
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matisshell_ MATISSHELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matisshell_ matisshell
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matshellgetcontext_(Mat mat,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatShellGetContext(
	(Mat)PetscToPointer((mat) ),ctx);
}
PETSC_EXTERN void  matshellsetcontext_(Mat mat,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatShellSetContext(
	(Mat)PetscToPointer((mat) ),ctx);
}
PETSC_EXTERN void  matshellsetmanagescalingshifts_(Mat A, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
*ierr = MatShellSetManageScalingShifts(
	(Mat)PetscToPointer((A) ));
}
PETSC_EXTERN void  matisshell_(Mat mat,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatIsShell(
	(Mat)PetscToPointer((mat) ),flg);
}
#if defined(__cplusplus)
}
#endif
