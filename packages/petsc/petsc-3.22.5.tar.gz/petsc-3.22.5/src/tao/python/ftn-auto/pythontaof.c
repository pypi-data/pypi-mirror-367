#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pythontao.c */
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

#include "petsctao.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taopythonsettype_ TAOPYTHONSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taopythonsettype_ taopythonsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define taopythongettype_ TAOPYTHONGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define taopythongettype_ taopythongettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  taopythonsettype_(Tao tao, char pyname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tao);
/* insert Fortran-to-C conversion for pyname */
  FIXCHAR(pyname,cl0,_cltmp0);
*ierr = TaoPythonSetType(
	(Tao)PetscToPointer((tao) ),_cltmp0);
  FREECHAR(pyname,_cltmp0);
}
PETSC_EXTERN void  taopythongettype_(Tao tao, char *pyname, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tao);
*ierr = TaoPythonGetType(
	(Tao)PetscToPointer((tao) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for pyname */
*ierr = PetscStrncpy(pyname, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, pyname, cl0);
}
#if defined(__cplusplus)
}
#endif
