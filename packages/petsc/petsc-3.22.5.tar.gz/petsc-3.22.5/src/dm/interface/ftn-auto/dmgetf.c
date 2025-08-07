#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmget.c */
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

#include "petscdm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlocalvector_ DMGETLOCALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlocalvector_ dmgetlocalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmrestorelocalvector_ DMRESTORELOCALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmrestorelocalvector_ dmrestorelocalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetglobalvector_ DMGETGLOBALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetglobalvector_ dmgetglobalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearglobalvectors_ DMCLEARGLOBALVECTORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearglobalvectors_ dmclearglobalvectors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearlocalvectors_ DMCLEARLOCALVECTORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearlocalvectors_ dmclearlocalvectors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmrestoreglobalvector_ DMRESTOREGLOBALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmrestoreglobalvector_ dmrestoreglobalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearnamedglobalvectors_ DMCLEARNAMEDGLOBALVECTORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearnamedglobalvectors_ dmclearnamedglobalvectors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearnamedlocalvectors_ DMCLEARNAMEDLOCALVECTORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearnamedlocalvectors_ dmclearnamedlocalvectors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhasnamedglobalvector_ DMHASNAMEDGLOBALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhasnamedglobalvector_ dmhasnamedglobalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetnamedglobalvector_ DMGETNAMEDGLOBALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetnamedglobalvector_ dmgetnamedglobalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmrestorenamedglobalvector_ DMRESTORENAMEDGLOBALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmrestorenamedglobalvector_ dmrestorenamedglobalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhasnamedlocalvector_ DMHASNAMEDLOCALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhasnamedlocalvector_ dmhasnamedlocalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetnamedlocalvector_ DMGETNAMEDLOCALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetnamedlocalvector_ dmgetnamedlocalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmrestorenamedlocalvector_ DMRESTORENAMEDLOCALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmrestorenamedlocalvector_ dmrestorenamedlocalvector
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmgetlocalvector_(DM dm,Vec *g, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool g_null = !*(void**) g ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(g);
*ierr = DMGetLocalVector(
	(DM)PetscToPointer((dm) ),g);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! g_null && !*(void**) g) * (void **) g = (void *)-2;
}
PETSC_EXTERN void  dmrestorelocalvector_(DM dm,Vec *g, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool g_null = !*(void**) g ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(g);
*ierr = DMRestoreLocalVector(
	(DM)PetscToPointer((dm) ),g);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! g_null && !*(void**) g) * (void **) g = (void *)-2;
}
PETSC_EXTERN void  dmgetglobalvector_(DM dm,Vec *g, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool g_null = !*(void**) g ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(g);
*ierr = DMGetGlobalVector(
	(DM)PetscToPointer((dm) ),g);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! g_null && !*(void**) g) * (void **) g = (void *)-2;
}
PETSC_EXTERN void  dmclearglobalvectors_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMClearGlobalVectors(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmclearlocalvectors_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMClearLocalVectors(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmrestoreglobalvector_(DM dm,Vec *g, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool g_null = !*(void**) g ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(g);
*ierr = DMRestoreGlobalVector(
	(DM)PetscToPointer((dm) ),g);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! g_null && !*(void**) g) * (void **) g = (void *)-2;
}
PETSC_EXTERN void  dmclearnamedglobalvectors_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMClearNamedGlobalVectors(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmclearnamedlocalvectors_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMClearNamedLocalVectors(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmhasnamedglobalvector_(DM dm, char *name,PetscBool *exists, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMHasNamedGlobalVector(
	(DM)PetscToPointer((dm) ),_cltmp0,exists);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetnamedglobalvector_(DM dm, char *name,Vec *X, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool X_null = !*(void**) X ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(X);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetNamedGlobalVector(
	(DM)PetscToPointer((dm) ),_cltmp0,X);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! X_null && !*(void**) X) * (void **) X = (void *)-2;
}
PETSC_EXTERN void  dmrestorenamedglobalvector_(DM dm, char *name,Vec *X, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool X_null = !*(void**) X ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(X);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMRestoreNamedGlobalVector(
	(DM)PetscToPointer((dm) ),_cltmp0,X);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! X_null && !*(void**) X) * (void **) X = (void *)-2;
}
PETSC_EXTERN void  dmhasnamedlocalvector_(DM dm, char *name,PetscBool *exists, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMHasNamedLocalVector(
	(DM)PetscToPointer((dm) ),_cltmp0,exists);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetnamedlocalvector_(DM dm, char *name,Vec *X, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool X_null = !*(void**) X ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(X);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetNamedLocalVector(
	(DM)PetscToPointer((dm) ),_cltmp0,X);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! X_null && !*(void**) X) * (void **) X = (void *)-2;
}
PETSC_EXTERN void  dmrestorenamedlocalvector_(DM dm, char *name,Vec *X, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool X_null = !*(void**) X ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(X);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMRestoreNamedLocalVector(
	(DM)PetscToPointer((dm) ),_cltmp0,X);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! X_null && !*(void**) X) * (void **) X = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
