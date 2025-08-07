#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* pcset.c */
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
#define pcsettype_ PCSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsettype_ pcsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgettype_ PCGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgettype_ pcgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetfromoptions_ PCSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetfromoptions_ pcsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetdm_ PCSETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetdm_ pcsetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetdm_ PCGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetdm_ pcgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcsetapplicationcontext_ PCSETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcsetapplicationcontext_ pcsetapplicationcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define pcgetapplicationcontext_ PCGETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define pcgetapplicationcontext_ pcgetapplicationcontext
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  pcsettype_(PC pc,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PCSetType(
	(PC)PetscToPointer((pc) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  pcgettype_(PC pc,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetType(
	(PC)PetscToPointer((pc) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  pcsetfromoptions_(PC pc, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetFromOptions(
	(PC)PetscToPointer((pc) ));
}
PETSC_EXTERN void  pcsetdm_(PC pc,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
CHKFORTRANNULLOBJECT(dm);
*ierr = PCSetDM(
	(PC)PetscToPointer((pc) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  pcgetdm_(PC pc,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = PCGetDM(
	(PC)PetscToPointer((pc) ),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  pcsetapplicationcontext_(PC pc,void*usrP, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCSetApplicationContext(
	(PC)PetscToPointer((pc) ),usrP);
}
PETSC_EXTERN void  pcgetapplicationcontext_(PC pc,void*usrP, int *ierr)
{
CHKFORTRANNULLOBJECT(pc);
*ierr = PCGetApplicationContext(
	(PC)PetscToPointer((pc) ),usrP);
}
#if defined(__cplusplus)
}
#endif
