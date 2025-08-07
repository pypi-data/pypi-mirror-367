#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* snescomposite.c */
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

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescompositesettype_ SNESCOMPOSITESETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescompositesettype_ snescompositesettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescompositeaddsnes_ SNESCOMPOSITEADDSNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescompositeaddsnes_ snescompositeaddsnes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescompositegetsnes_ SNESCOMPOSITEGETSNES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescompositegetsnes_ snescompositegetsnes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescompositegetnumber_ SNESCOMPOSITEGETNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescompositegetnumber_ snescompositegetnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define snescompositesetdamping_ SNESCOMPOSITESETDAMPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define snescompositesetdamping_ snescompositesetdamping
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  snescompositesettype_(SNES snes,SNESCompositeType *type, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESCompositeSetType(
	(SNES)PetscToPointer((snes) ),*type);
}
PETSC_EXTERN void  snescompositeaddsnes_(SNES snes,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(snes);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = SNESCompositeAddSNES(
	(SNES)PetscToPointer((snes) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  snescompositegetsnes_(SNES snes,PetscInt *n,SNES *subsnes, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
PetscBool subsnes_null = !*(void**) subsnes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subsnes);
*ierr = SNESCompositeGetSNES(
	(SNES)PetscToPointer((snes) ),*n,subsnes);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subsnes_null && !*(void**) subsnes) * (void **) subsnes = (void *)-2;
}
PETSC_EXTERN void  snescompositegetnumber_(SNES snes,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLINTEGER(n);
*ierr = SNESCompositeGetNumber(
	(SNES)PetscToPointer((snes) ),n);
}
PETSC_EXTERN void  snescompositesetdamping_(SNES snes,PetscInt *n,PetscReal *dmp, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
*ierr = SNESCompositeSetDamping(
	(SNES)PetscToPointer((snes) ),*n,*dmp);
}
#if defined(__cplusplus)
}
#endif
