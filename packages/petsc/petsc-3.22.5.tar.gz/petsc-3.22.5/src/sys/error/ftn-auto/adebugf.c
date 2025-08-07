#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* adebug.c */
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
#define petscsetdebugterminal_ PETSCSETDEBUGTERMINAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsetdebugterminal_ petscsetdebugterminal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsetdebugger_ PETSCSETDEBUGGER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsetdebugger_ petscsetdebugger
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsetdefaultdebugger_ PETSCSETDEFAULTDEBUGGER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsetdefaultdebugger_ petscsetdefaultdebugger
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsetdebuggerfromstring_ PETSCSETDEBUGGERFROMSTRING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsetdebuggerfromstring_ petscsetdebuggerfromstring
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscwaitonerror_ PETSCWAITONERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscwaitonerror_ petscwaitonerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscattachdebugger_ PETSCATTACHDEBUGGER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscattachdebugger_ petscattachdebugger
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscstopfordebugger_ PETSCSTOPFORDEBUGGER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscstopfordebugger_ petscstopfordebugger
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsetdebugterminal_( char terminal[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for terminal */
  FIXCHAR(terminal,cl0,_cltmp0);
*ierr = PetscSetDebugTerminal(_cltmp0);
  FREECHAR(terminal,_cltmp0);
}
PETSC_EXTERN void  petscsetdebugger_( char debugger[],PetscBool *usedebugterminal, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for debugger */
  FIXCHAR(debugger,cl0,_cltmp0);
*ierr = PetscSetDebugger(_cltmp0,*usedebugterminal);
  FREECHAR(debugger,_cltmp0);
}
PETSC_EXTERN void  petscsetdefaultdebugger_(int *ierr)
{
*ierr = PetscSetDefaultDebugger();
}
PETSC_EXTERN void  petscsetdebuggerfromstring_( char string[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
/* insert Fortran-to-C conversion for string */
  FIXCHAR(string,cl0,_cltmp0);
*ierr = PetscSetDebuggerFromString(_cltmp0);
  FREECHAR(string,_cltmp0);
}
PETSC_EXTERN void  petscwaitonerror_(int *ierr)
{
*ierr = PetscWaitOnError();
}
PETSC_EXTERN void  petscattachdebugger_(int *ierr)
{
*ierr = PetscAttachDebugger();
}
PETSC_EXTERN void  petscstopfordebugger_(int *ierr)
{
*ierr = PetscStopForDebugger();
}
#if defined(__cplusplus)
}
#endif
